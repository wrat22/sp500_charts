import psycopg2
from dotenv import load_dotenv
import os
import yfinance as yf


def main():
    load_dotenv()

    db_name = os.getenv("DBNAME")
    db_user = os.getenv("DBUSER")
    db_password = os.getenv("DBPASSWORD")

    if not db_name or not db_user or not db_password:
        print("Database configuration environment variables are missing")
        return

    try:
        with psycopg2.connect(database=db_name, user=db_user, password=db_password) as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT ticker FROM companies;""")
                company_tickers = cur.fetchall()
                conn.commit()
            company_tickers_list = [str(row[0]) for row in company_tickers]

            for ticker in company_tickers_list:
                get_stock_data(ticker)

    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(start='2010-01-01', end='2024-07-16', interval='1wk')
        hist.to_csv(f"data/{ticker}.csv")
    except Exception as e:
        print(f"Failed to save stock data for {ticker}: {e}")


if __name__ == "__main__":
    main()
