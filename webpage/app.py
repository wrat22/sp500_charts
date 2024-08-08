import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import plotly.express as px
import pandas as pd


app = Flask(__name__)

load_dotenv()
DB_USER = os.getenv('DBUSER')
DB_PASSWORD = os.getenv('DBPASSWORD')
DB_HOST = os.getenv('DBHOST')
DB_PORT = os.getenv('DBPORT')
DB_NAME = os.getenv('DBNAME')
pandas_value_df = pd.read_sql(f"SELECT ticker, date, close FROM stock_prize", f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
pandas_companies_df = pd.read_sql(f"SELECT ticker, name FROM companies", f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")


@app.route('/')
def index():
    return render_template('index.html', stocks=list(pandas_companies_df['name'].unique()))


@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    name = request.form['ticker']
    matching_rows = pandas_companies_df.loc[pandas_companies_df['name'] == name, 'ticker']
    if not matching_rows.empty:
        ticker = matching_rows.iloc[0]
        if ticker in pandas_value_df['ticker'].unique():
            data = pandas_value_df[pandas_value_df['ticker'] == ticker]
            pct_change = calculate_pct_change(pandas_value_df, ticker)
            fig = px.line(data, x='date', y='close', title=f'${ticker} Stock Prices')
            graphJSON = fig.to_json()
            return jsonify({"graph": graphJSON, "pct_change": pct_change, "name": name})
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


if __name__ == "__main__":
    app.run(debug=True)
