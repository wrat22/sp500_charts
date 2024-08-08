import logging
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import numpy as np
from psycopg2.extensions import register_adapter, AsIs

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

register_adapter(np.int64, AsIs)
register_adapter(np.float64, AsIs)

default_args = {
    'owner': 'wrat',
    'retries': 5,
    'retry_delay': timedelta(minutes=10)
}


def main(ds_nodash):
    tickers = get_tickers()
    company_tickers = [str(row[0]) for row in tickers]
    for ticker in company_tickers:
        data = get_ticker_data(ticker, ds_nodash)
        if data is not None:
            cleaned_data = clean_data(data, ticker)
            if cleaned_data is not None:
                save_data_to_db(cleaned_data)


def get_tickers():
    hook = PostgresHook(postgres_conn_id="postgres_localhost")
    try:
        conn = hook.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT ticker FROM companies")
        company_tickers = cur.fetchall()
        cur.close()
        conn.close()
        logging.info("Successfully connected to db")
        return company_tickers
    except Exception as e:
        logging.error(f"Error {e} Connecting to db failed")
        return []


def get_ticker_data(ticker, ds_nodash):
    try:
        stock = yf.Ticker(ticker)
        close_data = datetime.strptime(ds_nodash, '%Y%m%d')
        end_data = close_data + timedelta(days=1)
        data = stock.history(start=close_data, end=end_data)
        logging.info(f"Got data for {ticker}")
        return data
    except Exception as e:
        logging.error(f"Error: {e} while getting ticker data")
        return None


def clean_data(raw_data, ticker):
    try:
        data1 = raw_data.drop(columns=['Stock Splits', 'Dividends'])
        data1['Open'] = data1['Open'].apply(lambda x: round(x, 2))
        data1['Close'] = data1['Close'].apply(lambda x: round(x, 2))
        data1['High'] = data1['High'].apply(lambda x: round(x, 2))
        data1['Low'] = data1['Low'].apply(lambda x: round(x, 2))
        data1['date'] = data1.index
        data1.reset_index()
        data1['date'] = pd.to_datetime(data1['date']).dt.date
        data1.rename(columns={
            'Close': 'close',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Volume': 'volume'
        }, inplace=True)
        data1['ticker'] = ticker
        data1.head()
        logging.info("Data cleaned successfully")
        return data1
    except Exception as e:
        logging.error(f"Error: {e} while cleaning data")
        return None


def save_data_to_db(data):
    hook = PostgresHook(postgres_conn_id="postgres_localhost")
    try:
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO stock_prize (ticker, date, open, high, low, close, volume)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                            """, (
                            data['ticker'].values[0], data['date'].values[0], data['open'].values[0],
                            data['high'].values[0], data['low'].values[0], data['close'].values[0],
                            data['volume'].values[0]
                ))
                conn.commit()
                logging.info(f"Imported database with data about {data['ticker'].values[0]}")
    except Exception as e:
        logging.error(f"Error: {e} while saving to db")


with DAG(
    dag_id="dag_update_postgres_ver_final",
    default_args=default_args,
    start_date=datetime(2024, 7, 19),
    schedule_interval='0 10 * * Fri'
) as dag:
    task_update_database = PythonOperator(
        task_id="postgres_connection",
        python_callable=main
    )
    task_update_database
