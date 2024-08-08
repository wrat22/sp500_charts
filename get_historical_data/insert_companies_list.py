import json
import psycopg2
from dotenv import load_dotenv
import os


def main():
    companies_list = get_companies()
    insert_companies(companies_list)


def get_companies():
    with open('List_of_S&P_500_companies.json') as f:
        data = json.load(f)
        data = data[0]
        headers = data[0]
        company_list = []
        for row in data[1:]:
            company = {headers[i]: row[i] for i in range(len(headers))}
            company_list.append(company)
    return company_list


def insert_companies(company_list):
    load_dotenv()
    db_name = os.getenv("DBNAME")
    db_user = os.getenv("DBUSER")
    db_password = os.getenv("DBPASSWORD")
    conn = psycopg2.connect(database=db_name, user=db_user, password=db_password)
    cur = conn.cursor()
    for company in company_list:
        cur.execute("""
            INSERT INTO companies (ticker, name, sector, industry)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (ticker) DO NOTHING;
        """, (company['Symbol'], company['Security'], company['GICS Sub-Industry'], company['GICS Sector']))
    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
