import numpy as np
import pandas as pd
from flask import Blueprint, render_template, request, jsonify, current_app as app
import plotly.express as px
import plotly.graph_objects as go

from utils import (
    calculate_last_change,
    filter_by_range,
    calculate_pct_change_for_range,
    get_value,
)
from models import (
    get_stock_values_from_db,
    get_stock_companies_from_db,
    get_last_update_from_db,
)
from extensions import cache

main_routes = Blueprint("main_routes", __name__)


def get_cached_stock_companies():
    cache_key = 'companies_data'

    cached_data = cache.get(cache_key)
    if cached_data is None:
        cached_data = get_stock_companies_from_db()
        cache.set(cache_key, cached_data, timeout=60)

    return cached_data


def get_cached_stock_values():
    cache_key = 'values_data'

    cached_data = cache.get(cache_key)
    if cached_data is None:
        cached_data = get_stock_values_from_db()
        cache.set(cache_key, cached_data, timeout=60)

    return cached_data


@main_routes.route("/")
def index():
    """
    Route handler for the root URL ('/')

    Retrieves stock company data from database and renders 'index.html' template with
    the list of unique stock company names and the last update date.

    :return:
        Response: A Flask 'Response' object that renders the 'index.html' template with the:
            - 'stocks' (list of str): List of unique stock company names.
            - 'last_update' (str): The date of the last update in 'YYYY-MM-DD' format.
    """
    pandas_companies_df = get_cached_stock_companies()

    try:
        if pandas_companies_df is None:
            raise Exception("Data could not be loaded from database.")

        last_update_df = get_last_update_from_db()
        last_update = last_update_df["date"].max()
        last_update_str = last_update.strftime("%Y-%m-%d")

        return render_template(
            "index.html",
            stocks=list(pandas_companies_df["name"].unique()),
            last_update=last_update_str,
        )
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({"Database error": str(e)}), 500


@main_routes.route("/get_stock_data", methods=["POST"])
def get_stock_data():
    """
    Route handler for the  URL ('/get_stock_data')

    Process a request to retrieve stock data for a given company ticker.

    :parameter:
        - 'ticker' (str): the name of the company for which stock is requested.
        - 'range' (str): the data range for filtering the stock data.
    :return:
        Response: A Flask 'Response' object with a JSON payload containing:
            - 'graph' (str): A JSON string representation of the line chart of stock prices.
            - 'pct-change' (float): the percentage change in stock price.
            - 'name' (str): the company name provided in the request.
            - 'ticker' (str): the company ticker symbol.
            - 'last_value' (int or float): the stock value from last week.
    """
    name = request.form["ticker"]
    range_option = request.form["range"]

    pandas_companies_df = get_cached_stock_companies()
    pandas_value_df = get_cached_stock_values()

    matching_rows = pandas_companies_df.loc[
        pandas_companies_df["name"] == name, "ticker"
    ]

    if not matching_rows.empty:
        ticker = matching_rows.iloc[0]

        if ticker in pandas_value_df["ticker"].unique():
            data = pandas_value_df[pandas_value_df["ticker"] == ticker].copy()

            data = filter_by_range(data, range_option)

            pct_change = calculate_pct_change_for_range(data, ticker)

            last_change = calculate_last_change(data, ticker)

            last_value = get_value(data, ticker)

            fig = px.line(data, x="date", y="close")
            graphJSON = fig.to_json()

            stored_first_data = data

            return jsonify(
                {
                    "graph": graphJSON,
                    "pct_change": pct_change,
                    "name": name,
                    "ticker": ticker,
                    "last_change": last_change,
                    "last_value": last_value,
                }
            )
        else:
            return jsonify({"error": "Stock ticker not found"})
    else:
        return jsonify({"error": "Company name not found"})


@main_routes.route("/compare_stocks", methods=["POST"])
def compare_stocks():
    """
    Route handler for the  URL ('/compare_stocks')

    Compare stock prices for two given companies and generates a line chart showing historical stock values.

    :parameter:
        - 'first_ticker' (str): the name of the first company to compare.
        - 'second_ticker' (str): the name of the second company to compare
        - 'range' (str): the data range for filtering the stock data.
    :return:
        Response: A Flask 'Response' object with a JSON payload containing:
            - 'graph' (str): A JSON string representation of the line chart of stock prices.
    """
    first_ticker = request.form["first_ticker"]
    second_ticker = request.form["second_ticker"]
    range_option = request.form["range"]

    pandas_companies_df = get_cached_stock_companies()
    pandas_value_df = get_cached_stock_values()

    if "stored_first_date" in globals() and stored_first_data is not None:
        first_data = stored_first_data
        first_last_value = stored_first_data["close"].iloc[-1]
        first_pct_change = calculate_pct_change_for_range(first_data, first_ticker)
    else:
        matching_first_rows = pandas_companies_df.loc[
            pandas_companies_df["name"] == first_ticker, "ticker"
        ]
        if not matching_first_rows.empty:
            first_ticker_symbol = matching_first_rows.iloc[0]
            first_data = pandas_value_df[
                pandas_value_df["ticker"] == first_ticker_symbol
            ].copy()
            first_data = filter_by_range(first_data, range_option)

            first_last_value = first_data["close"].iloc[-1]
            first_pct_change = calculate_pct_change_for_range(first_data, first_ticker_symbol)
            first_last_change = calculate_last_change(first_data, first_ticker_symbol)
        else:
            return jsonify({"error": "First company name not found"})

    matching_second_rows = pandas_companies_df.loc[
        pandas_companies_df["name"] == second_ticker, "ticker"
    ]
    if not matching_second_rows.empty:
        second_ticker_symbol = matching_second_rows.iloc[0]
        second_data = pandas_value_df[
            pandas_value_df["ticker"] == second_ticker_symbol
        ].copy()
        second_data = filter_by_range(second_data, range_option)

        second_last_value = second_data["close"].iloc[-1]
        second_pct_change = calculate_pct_change_for_range(second_data, second_ticker_symbol)
        second_last_change = calculate_last_change(second_data, second_ticker_symbol)
    else:
        return jsonify({"error": "Second company name not found"})

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=first_data["date"],
            y=first_data["close"],
            mode="lines",
            name=first_ticker,
            line=dict(color="blue"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=second_data["date"],
            y=second_data["close"],
            mode="lines",
            name=second_ticker,
            line=dict(color="red"),
        )
    )

    fig.update_layout(
        title=f"{first_ticker} vs {second_ticker} Stock Prizes",
        xaxis_title="Date",
        yaxis_title="Price",
    )

    graphJSON = fig.to_json()

    response_data = {
        "graph": graphJSON,
        "first_stock": {
            "name": first_ticker_symbol,
            "last_value": first_last_value,
            "last_change": first_last_change,
            "pct_change": first_pct_change
        },
        "second_stock": {
            "name": second_ticker_symbol,
            "last_value": second_last_value,
            "last_change": second_last_change,
            "pct_change": second_pct_change
        }
    }

    return jsonify(response_data)
