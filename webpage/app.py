import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import plotly.express as px
import pandas as pd
import psycopg2


app = Flask(__name__)

load_dotenv()
DB_USER = os.getenv('DBUSER')
DB_PASSWORD = os.getenv('DBPASSWORD')
DB_HOST = os.getenv('DBHOST')
DB_PORT = os.getenv('DBPORT')
DB_NAME = os.getenv('DBNAME')

try:
    with psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASSWORD) as conn:
        with conn.cursor() as cur:
            sql = pd.read_sql_query("SELECT ticker, name FROM companies", conn)
            pandas_companies_df = pd.DataFrame(sql, columns=["ticker", "name"])
            sql2 = pd.read_sql_query("SELECT ticker, date, close FROM stock_prize", conn)
            pandas_value_df = pd.DataFrame(sql2, columns=["ticker", "date", "close"])
except psycopg2.Error as e:
    print(f"Database error: {e}")


@app.route('/')
def index():
    last_update = pandas_value_df['date'].max()

    last_update_str = last_update.strftime('%Y-%m-%d')

    return render_template('index.html', stocks=list(pandas_companies_df['name'].unique()), last_update=last_update_str)


@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    name = request.form['ticker']
    matching_rows = pandas_companies_df.loc[pandas_companies_df['name'] == name, 'ticker']
    if not matching_rows.empty:
        ticker = matching_rows.iloc[0]
        if ticker in pandas_value_df['ticker'].unique():
            data = pandas_value_df[pandas_value_df['ticker'] == ticker]
            pct_change = calculate_pct_change(pandas_value_df, ticker)
            last_week_value = calculate_last_week(pandas_value_df, ticker)
            fig = px.line(data, x='date', y='close', title=f'${ticker} Stock Prices')
            graphJSON = fig.to_json()
            return jsonify({"graph": graphJSON,
                            "pct_change": pct_change,
                            "name": name,
                            "ticker": ticker,
                            "last_week_value": last_week_value})
        else:
            return jsonify({"error": "Stock ticker not found"})
    else:
        return jsonify({"error": "Company name not found"})


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

if __name__ == "__main__":
    app.run(debug=True)
