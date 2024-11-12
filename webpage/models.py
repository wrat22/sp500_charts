import os

from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine

from utils import filter_by_range

load_dotenv()
DB_USER = os.getenv("DBUSER")
DB_PASSWORD = os.getenv("DBPASSWORD")
DB_NAME = os.getenv("DBNAME")
DB_HOST = os.getenv("DBHOST")
DB_PORT = os.getenv("DBPORT")

DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URI)


def get_stock_values_from_db():
    """
    Retrieves stock values from the database and returns them as a pandas DataFrame
    :return:
        - df (pandas.DataFrame) or None: A DataFrame containing columns 'ticker', 'data', 'close'
        with the stock values retrieved from the database.
        If error occurs while loading data, the function returns None
    """
    df = None
    query = "SELECT ticker, date, close FROM stock_prize ORDER BY date ASC"
    try:
        with engine.connect() as conn:
            df = pd.read_sql(sql=query, con=conn.connection)
        return df
    except Exception as e:
        print(f"Database error: {e}")
        return None


def get_stock_companies_from_db():
    """
    Retrieves stock companies from the database and returns them as a pandas DataFrame
    :return:
        - df (pandas.DataFrame) or None: A DataFrame containing columns 'ticker', 'name'
        retrieved from the database. If error occurs while loading data, the function returns None
    """
    df = None
    query = "SELECT ticker, name FROM companies"
    try:
        with engine.connect() as conn:
            df = pd.read_sql(sql=query, con=conn.connection)
        return df
    except Exception as e:
        print(f"Database error: {e}")
        return None


def get_last_update_from_db():
    """
    Retrieves last update date from the database and returns them as a pandas DataFrame
    :return:
        - df (pandas.DataFrame) or None: A DataFrame containing columns 'date', 'ticker'
        retrieved from the database. If error occurs while loading data, the function returns None
    """
    df = None
    query = "SELECT date, ticker FROM stock_prize ORDER BY date DESC LIMIT 1"
    try:
        with engine.connect() as conn:
            df = pd.read_sql(sql=query, con=conn.connection)
        return df
    except Exception as e:
        print(f"Database error: {e}")
        return None
