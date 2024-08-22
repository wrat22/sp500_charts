import os

from dotenv import load_dotenv
import pandas as pd
import psycopg2

from utils import filter_by_range


def get_stock_values_from_db():
    load_dotenv()
    DB_USER = os.getenv('DBUSER')
    DB_PASSWORD = os.getenv('DBPASSWORD')
    DB_NAME = os.getenv('DBNAME')

    df = None

    try:
        with psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASSWORD) as conn:
            with conn.cursor() as cur:
                query = "SELECT ticker, date, close FROM stock_prize"
                sql = pd.read_sql_query(query, conn)
                df = pd.DataFrame(sql, columns=["ticker", "date", "close"])

                if df.empty:
                    return None

                df['date'] = pd.to_datetime(df['date'])

                return df
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")


def get_stock_companies_from_db():
    load_dotenv()
    DB_USER = os.getenv('DBUSER')
    DB_PASSWORD = os.getenv('DBPASSWORD')
    DB_NAME = os.getenv('DBNAME')

    df = None

    try:
        with psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASSWORD) as conn:
            with conn.cursor() as cur:
                query = "SELECT ticker, name FROM companies"
                sql = pd.read_sql_query(query, conn)
                df = pd.DataFrame(sql, columns=["ticker", "name"])
                if df.empty:
                    return None
                else:
                    return df
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")


def get_last_update_from_db():
    # TODO configure reading from db last_updated date
    load_dotenv()
    DB_USER = os.getenv('DBUSER')
    DB_PASSWORD = os.getenv('DBPASSWORD')
    DB_NAME = os.getenv('DBNAME')

    try:
        with psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASSWORD) as conn:
            with conn.cursor() as cur:
                query = "SELECT date, ticker FROM stock_prize ORDER BY date DESC LIMIT 1"
                sql = pd.read_sql_query(query, conn)
                df = pd.DataFrame(sql, columns=["date", "ticker"])
            if df.empty:
                return None
            else:
                return df
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
