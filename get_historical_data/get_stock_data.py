import psycopg2
from dotenv import load_dotenv
import os
import yfinance as yf


def main():
    load_dotenv()
    db_name = os.getenv("DBNAME")
    db_user = os.getenv("DBUSER")
    db_password = os.getenv("DBPASSWORD")
    conn = psycopg2.connect(database=db_name, user=db_user, password=db_password)
    cur = conn.cursor()
    cur.execute("""SELECT ticker FROM companies;""")
    company_tickers = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    company_tickers_list = [str(row[0]) for row in company_tickers]
    for ticker in company_tickers_list:
        get_stock_data(ticker)


def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(start='2010-01-01', end='2024-07-16', interval='1wk')
    hist.to_csv(f"data/{ticker}.csv")


if __name__ == "__main__":
    main()
