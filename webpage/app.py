import os

import numpy as np
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import psycopg2
from datetime import datetime, timedelta


app = Flask(__name__)

load_dotenv()
DB_USER = os.getenv('DBUSER')
DB_PASSWORD = os.getenv('DBPASSWORD')
DB_HOST = os.getenv('DBHOST')
DB_PORT = os.getenv('DBPORT')
DB_NAME = os.getenv('DBNAME')

pandas_companies_df = None
pandas_value_df = None

try:
    with psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASSWORD) as conn:
        with conn.cursor() as cur:
            sql = pd.read_sql_query("SELECT ticker, name FROM companies", conn)
            pandas_companies_df = pd.DataFrame(sql, columns=["ticker", "name"])
            sql2 = pd.read_sql_query("SELECT ticker, date, close FROM stock_prize", conn)
            pandas_value_df = pd.DataFrame(sql2, columns=["ticker", "date", "close"])
except psycopg2.Error as e:
    raise Exception(f"Database error: {e}")


@app.route('/')
def index():
    try:
        if pandas_value_df is None or pandas_companies_df is None:
            raise Exception("Data could not be loaded from database.")

        last_update = pandas_value_df['date'].max()
        last_update_str = last_update.strftime('%Y-%m-%d')

        return render_template('index.html', stocks=list(pandas_companies_df['name'].unique()), last_update=last_update_str)
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({"Database error": str(e)}), 500


@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    name = request.form['ticker']
    range_option = request.form['range']

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


@app.route('/compare_stocks', methods=['POST'])
def compare_stocks():
    first_ticker = request.form['first_ticker']
    second_ticker = request.form['second_ticker']
    range_option = request.form['range']

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
    fig.add_trace(go.Scatter(x=first_data['date'], y=first_data['close'], mode='lines', name=first_ticker, line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=second_data['date'], y=second_data['close'], mode='lines', name=second_ticker, line=dict(color='red')))

    fig.update_layout(title=f'{first_ticker} vs {second_ticker} Stock Prizes', xaxis_title='Date', yaxis_title='Price')

    graphJSON = fig.to_json()

    return jsonify({'graph': graphJSON})


def calculate_pct_change(df, ticker):
    ticker_data = df[df['ticker'] == ticker]
    last_week_close = ticker_data.iloc[-1]['close']
    week_before_lastweek = ticker_data.iloc[-2]['close']
    pct_change = ((last_week_close - week_before_lastweek) / week_before_lastweek) * 100
    return pct_change


def calculate_last_week(df, ticker):
    ticker_data = df[df['ticker'] == ticker]
    last_week_close = ticker_data.iloc[-1]['close']
    return last_week_close


def filter_by_range(data, range_option):
    today = datetime.today()

    if range_option == '3months':
        start_date = today - timedelta(days=90)
    elif range_option == '6months':
        start_date = today - timedelta(days=180)
    elif range_option == 'thisyear':
        start_date = datetime(today.year, 1, 1)
    elif range_option == '1year':
        start_date = today - timedelta(days=365)
    elif range_option == '3year':
        start_date = today - timedelta(days=1095)
    elif range_option == '5year':
        start_date = today - timedelta(days=1825)
    else:
        return data

    data['date'] = pd.to_datetime(data['date'])
    filtered_data = data[data['date'] >= start_date]

    return filtered_data


if __name__ == "__main__":
    app.run(debug=True)
