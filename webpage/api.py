from flask import Blueprint, render_template, request, jsonify

from models import (
    get_stock_values_from_db,
    get_stock_companies_from_db,
    get_last_update_from_db,
)
from utils import filter_by_range

api_routes = Blueprint("api_routes", __name__)


@api_routes.route("/api/stock<ticker>", methods=["GET"])
def get_stock_data_api(ticker):
    """
    Api route handler for ('api/stock<ticker>') with GET method

    Retrieves stock data for a specific ticker symbol and returns it in JSON format

    :parameter:
        - 'ticker' (str): the name of the company for which stock is requested.
        - 'range' (str, optional): the data range for filtering the stock data.
    :return:
        Response: A Flask 'Response' object with a JSON payload containing:
            - A list of dictionaries where each dictionary represents a record of
            stock data with fields such as date, ticker, and price.
    """
    range_option = request.args.get("range", default="all")

    pandas_companies_df = get_stock_companies_from_db()
    pandas_value_df = get_stock_values_from_db()

    matching_rows = pandas_companies_df.loc[pandas_companies_df["ticker"] == ticker]

    if matching_rows.empty:
        return abort(404, description="Stock ticker not found")

    data = pandas_value_df[pandas_value_df["ticker"] == ticker].copy()
    data = filter_by_range(data, range_option)
    data = data.sort_values(by="date")

    return jsonify(data.to_dict(orient="records"))


@api_routes.route("/api/compare_stocks", methods=["GET"])
def compare_stocks_api():
    """
    Api route handler for ('api/compare_stocks') with GET method

    Compares stock data for two given tickers and return their historical stock prices
    over a specified data range in JSON format.

    :parameter:
        - 'first_ticker' (str): the name of the first stock to compare.
        - 'second_ticker' (str): the name of the second stock to compare.
        - 'range' (str, optional): the data range for filtering the stock data. Defaults to 'all'.
    :return:
        Response: A Flask 'Response' object with a JSON payload containing:
            - 'first_ticker' (str): The ticker symbol for the first stock.
            - 'first_data' (list of dicts): A list of dictionaries where each dictionary represents.
            a record of stock data for the first ticker.
            - 'second_ticker' (str): The ticker symbol for the second stock.
            - 'second_data' (list of dicts): A list of dictionaries where each dictionary represents.
            a record of stock data for the second ticker.
    """
    first_ticker = request.args.get("first_ticker")
    second_ticker = request.args.get("second_ticker")
    range_option = request.args.get("range", default="all")

    pandas_companies_df = get_stock_companies_from_db()
    pandas_value_df = get_stock_values_from_db()

    first_matching_rows = pandas_companies_df.loc[
        pandas_companies_df["ticker"] == first_ticker
    ]
    second_matching_rows = pandas_companies_df.loc[
        pandas_companies_df["ticker"] == second_ticker
    ]

    if first_matching_rows.empty or second_matching_rows.empty:
        return abort(404, description="One or both stock tickers not found")

    first_data = pandas_value_df[pandas_value_df["ticker"] == first_ticker].copy()
    first_data = filter_by_range(first_data, range_option)
    first_data = first_data.sort_values(by="date")

    second_data = pandas_value_df[pandas_value_df["ticker"] == second_ticker].copy()
    second_data = filter_by_range(second_data, range_option)
    second_data = second_data.sort_values(by="date")

    return jsonify(
        {
            "first_ticker": first_ticker,
            "first_data": first_data.to_dict(orient="records"),
            "second_ticker": second_ticker,
            "second_data": second_data.to_dict(orient="records"),
        }
    )
