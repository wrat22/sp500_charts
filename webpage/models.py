import os

from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine

from utils import filter_by_range

load_dotenv()
DB_USER = os.getenv('DBUSER')
DB_PASSWORD = os.getenv('DBPASSWORD')
DB_NAME = os.getenv('DBNAME')
DB_HOST = os.getenv('DBHOST')
DB_PORT = os.getenv('DBPORT')

DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URI)


def get_stock_values_from_db():
    df = None
    query = "SELECT ticker, date, close FROM stock_prize"
    try:
        with engine.connect() as conn:
            df = pd.read_sql(sql=query, con=conn.connection)
        return df
    except Exception as e:
        print(f"Database error: {e}")
        return None


def get_stock_companies_from_db():
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
    df = None
    query = "SELECT date, ticker FROM stock_prize ORDER BY date DESC LIMIT 1"
    try:
        with engine.connect() as conn:
            df = pd.read_sql(sql=query, con=conn.connection)
        return df
    except Exception as e:
        print(f"Database error: {e}")
        return None
