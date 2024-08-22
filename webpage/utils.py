from datetime import datetime, timedelta
import pandas as pd


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
