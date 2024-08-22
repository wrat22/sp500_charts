from flask import Blueprint, render_template, request, jsonify

from models import get_stock_values_from_db, get_stock_companies_from_db, get_last_update_from_db
from utils import filter_by_range

api_routes = Blueprint('api_routes', __name__)


@api_routes.route('/api/stock<ticker>', methods=['GET'])
def get_stock_data_api(ticker):
    range_option = request.args.get('range', default='all')

    pandas_companies_df = get_stock_companies_from_db()
    pandas_value_df = get_stock_values_from_db()

    matching_rows = pandas_companies_df.loc[pandas_companies_df['ticker'] == ticker]

    if matching_rows.empty:
        return abort(404, description="Stock ticker not found")

    data = pandas_value_df[pandas_value_df['ticker'] == ticker].copy()
    data = filter_by_range(data, range_option)
    data = data.sort_values(by='date')

    return jsonify(data.to_dict(orient='records'))


@api_routes.route('/api/compare_stocks', methods=['GET'])
def compare_stocks_api():
    first_ticker = request.args.get('first_ticker')
    second_ticker = request.args.get('second_ticker')
    range_option = request.args.get('range', default='all')

    pandas_companies_df = get_stock_companies_from_db()
    pandas_value_df = get_stock_values_from_db()

    first_matching_rows = pandas_companies_df.loc[pandas_companies_df['ticker'] == first_ticker]
    second_matching_rows = pandas_companies_df.loc[pandas_companies_df['ticker'] == second_ticker]

    if first_matching_rows.empty or second_matching_rows.empty:
        return abort(404, description="One or both stock tickers not found")

    first_data = pandas_value_df[pandas_value_df['ticker'] == first_ticker].copy()
    first_data = filter_by_range(first_data, range_option)
    first_data = first_data.sort_values(by='date')

    second_data = pandas_value_df[pandas_value_df['ticker'] == second_ticker].copy()
    second_data = filter_by_range(second_data, range_option)
    second_data = second_data.sort_values(by='date')

    return jsonify({
        "first_ticker": first_ticker,
        "first_data": first_data.to_dict(orient='records'),
        "second_ticker": second_ticker,
        "second_data": second_data.to_dict(orient='records')
    })
