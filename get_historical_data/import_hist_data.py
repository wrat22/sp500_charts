import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import to_date, round, lit


def main():
    spark = initialize_spark()
    DIRECTORY = "data"
    for filename in os.listdir(DIRECTORY):
        process_file(filename, spark)


def initialize_spark():
    spark = SparkSession.builder.appName("get_hist_data").getOrCreate()
    return spark


def process_file(filename, spark):
    ticker = filename[:-4]
    df = spark.read.option("header", "true").csv(f"data/{filename}", inferSchema=True)
    cleaned_data = clean_data(df, ticker)
    save_to_db(cleaned_data)
    return


def clean_data(df, ticker):
    df1 = df.drop("Dividends", "Stock Splits").withColumns(
        {
            "ticker": lit(ticker),
            "Open": round(df["Open"], 2),
            "High": round(df["High"], 2),
            "Low": round(df["Low"], 2),
            "Close": round(df["Close"], 2),
        }
    )
    df2 = df1.withColumn("Date", to_date(df1["Date"]))
    return df2


def save_to_db(df):
    load_dotenv()
    db_name = os.getenv("DBNAME")
    db_user = os.getenv("DBUSER")
    db_password = os.getenv("DBPASSWORD")
    db_server = os.getenv("DBHOST")
    db_port = os.getenv("DBPORT")
    db_table = "stock_prize"
    URL = f"jdbc:postgresql://{db_server}:{db_port}/{db_name}"
    df.write.format("jdbc").option("url", URL).option("dbtable", db_table).option("user", db_user).option("password", db_password).mode("append").save()


if __name__ == "__main__":
    main()
