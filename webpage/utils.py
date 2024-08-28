from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def filter_by_range(data, range_option):
    """
    Filters the provided stock data based on the specified data range.

    :parameter:
        - data: (pandas.DataFrame): A DataFrame containing stock data.
        - range_option (str): A string specifying the data range to filter the data.
    :return:
        - data: (pandas.DataFrame): A DataFrame containing only the rows where the 'date' is within the specified range.
    """
    today = datetime.today()

    if range_option == "3months":
        start_date = today - timedelta(days=90)
    elif range_option == "6months":
        start_date = today - timedelta(days=180)
    elif range_option == "thisyear":
        start_date = datetime(today.year, 1, 1)
    elif range_option == "1year":
        start_date = today - timedelta(days=365)
    elif range_option == "3year":
        start_date = today - timedelta(days=1095)
    elif range_option == "5year":
        start_date = today - timedelta(days=1825)
    else:
        return data

    data["date"] = pd.to_datetime(data["date"])
    filtered_data = data[data["date"] >= start_date]

    return filtered_data


def calculate_pct_change_for_range(data, ticker):
    """
        Calculates change in prize stocks between weeks

        :parameter:
            - df (pandas.DataFrame): A DataFrame containing stock data.
            - ticker (str): A company symbol for which change is calculated.
        :return:
            - pct_change: (float): the percentage change in stock prices.
        """
    ticker_data = data[data["ticker"] == ticker]
    if len(data) >= 2:
        last_close = ticker_data.iloc[-1]['close']
        first_close = ticker_data.iloc[0]['close']
        pct_change = ((last_close - first_close) / first_close) * 100
        return float(pct_change)
    return 0


def calculate_last_change(df, ticker):
    """
    Returns last week close value in stock prices for specified company.

    :parameter:
        - df (pandas.DataFrame): A DataFrame containing stock data.
        - ticker (str): A company symbol for which value is returned.
    :return:
        - last_week_close: (int): the stock value of last week.
    """
    ticker_data = df[df["ticker"] == ticker]
    if len(df) >= 2:
        last_close = ticker_data.iloc[-1]["close"]
        first_close = ticker_data.iloc[0]["close"]
        close_change = last_close - first_close
        close_change = (
            int(close_change)
            if isinstance(close_change, np.integer)
            else close_change
        )
        return close_change
    return 0


def get_value(df, ticker):
    ticker_data = df[df["ticker"] == ticker]
    last_close = ticker_data.iloc[-1]["close"]
    last_close = (
        int(last_close)
        if isinstance(last_close, np.integer)
        else last_close
    )
    return last_close
