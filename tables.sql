CREATE TABLE companies (
    ticker VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100)
);


CREATE TABLE stock_prize(
    id SERIAL PRIMARY KEY,
    ticker REFERENCES companies(thicker),
    date DATE NOT NULL,
    open DECIMAL(10, 2),
    high DECIMAL(10, 2),
    low DECIMAL(10, 2),
    close DECIMAL(10, 2),
    volume BIGINT,
    UNIQUE (ticker, date)
);