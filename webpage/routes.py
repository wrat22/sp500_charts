import numpy as np
import pandas as pd
from flask import Blueprint, render_template, request, jsonify
import plotly.express as px
import plotly.graph_objects as go

from utils import calculate_pct_change, calculate_last_week, filter_by_range
from models import get_stock_values_from_db, get_stock_companies_from_db, get_last_update_from_db

main_routes = Blueprint('main_routes', __name__)


@main_routes.route('/')
def index():
    pandas_companies_df = get_stock_companies_from_db()

    try:
        if pandas_companies_df is None:
            raise Exception("Data could not be loaded from database.")

        last_update_df = get_last_update_from_db()
        last_update = last_update_df['date'].max()
        last_update_str = last_update.strftime('%Y-%m-%d')

        return render_template('index.html', stocks=list(pandas_companies_df['name'].unique()),
                               last_update=last_update_str)
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({"Database error": str(e)}), 500


@main_routes.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    name = request.form['ticker']
    range_option = request.form['range']

    pandas_companies_df = get_stock_companies_from_db()
    pandas_value_df = get_stock_values_from_db()

    matching_rows = pandas_companies_df.loc[pandas_companies_df['name'] == name, 'ticker']

    if not matching_rows.empty:
        ticker = matching_rows.iloc[0]

        if ticker in pandas_value_df['ticker'].unique():
            data = pandas_value_df[pandas_value_df['ticker'] == ticker].copy()
            data = filter_by_range(data, range_option)
            data = data.sort_values(by='date')
            pct_change = calculate_pct_change(pandas_value_df, ticker)
            last_week_value = calculate_last_week(pandas_value_df, ticker)

            pct_change = float(pct_change)
            last_week_value = int(last_week_value) if isinstance(last_week_value, np.integer) else last_week_value

            fig = px.line(data, x='date', y='close', title=f'${ticker} Stock Prices')
            graphJSON = fig.to_json()

            stored_first_data = data

            return jsonify({"graph": graphJSON,
                            "pct_change": pct_change,
                            "name": name,
                            "ticker": ticker,
                            "last_week_value": last_week_value})
        else:
            return jsonify({"error": "Stock ticker not found"})
    else:
        return jsonify({"error": "Company name not found"})


@main_routes.route('/compare_stocks', methods=['POST'])
def compare_stocks():
    first_ticker = request.form['first_ticker']
    second_ticker = request.form['second_ticker']
    range_option = request.form['range']

    pandas_companies_df = get_stock_companies_from_db()
    pandas_value_df = get_stock_values_from_db()

    if 'stored_first_date' in globals() and stored_first_data is not None:
        first_data = stored_first_data
    else:
        matching_first_rows = pandas_companies_df.loc[pandas_companies_df['name'] == first_ticker, 'ticker']
        if not matching_first_rows.empty:
            first_ticker_symbol = matching_first_rows.iloc[0]
            first_data = pandas_value_df[pandas_value_df['ticker'] == first_ticker_symbol].copy()
            first_data = filter_by_range(first_data, range_option)
            first_data = first_data.sort_values(by='date')
        else:
            return jsonify({"error": "First company name not found"})

    matching_second_rows = pandas_companies_df.loc[pandas_companies_df['name'] == second_ticker, 'ticker']
    if not matching_second_rows.empty:
        second_ticker_symbol = matching_second_rows.iloc[0]
        second_data = pandas_value_df[pandas_value_df['ticker'] == second_ticker_symbol].copy()
        second_data = filter_by_range(second_data, range_option)
        second_data = second_data.sort_values(by='date')
    else:
        return jsonify({"error": "Second company name not found"})

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=first_data['date'], y=first_data['close'], mode='lines', name=first_ticker,
                             line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=second_data['date'], y=second_data['close'], mode='lines', name=second_ticker,
                             line=dict(color='red')))

    fig.update_layout(title=f'{first_ticker} vs {second_ticker} Stock Prizes', xaxis_title='Date', yaxis_title='Price')

    graphJSON = fig.to_json()

    return jsonify({'graph': graphJSON})
