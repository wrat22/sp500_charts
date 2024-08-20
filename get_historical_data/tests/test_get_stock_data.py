import os
import sys

import pandas as pd
import pytest
import psycopg2
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath((os.path.join(os.path.dirname(__file__), '..'))))

from get_stock_data import main, get_stock_data


@pytest.fixture
def mock_yfinance(mocker):
    mock_ticker = mocker.patch('get_stock_data.yf.Ticker')
    mock_stock = MagicMock()
    mock_stock.history.return_value = MagicMock()
    mock_ticker.return_value = mock_stock
    return mock_ticker


def test_missing_env_vars(mocker):
    mocker.patch.dict('os.environ', {
        "DBNAME": str(None),
        "DBUSER": str(None),
        "DBPASSWORD": str(None)
    }, clear=True)

    with pytest.raises(SystemExit):
        main()


def test_db_connection_failure(mocker):
    mocker.patch('psycopg2.connect', side_effect=psycopg2.OperationalError("Unable to connect"))

    mock_print = mocker.patch('builtins.print')

    main()

    mock_print.assert_called_once_with("Database error: Unable to connect")


def test_successful_fetching(mocker, mock_yfinance):
    mocker.patch.dict('os.environ', {
        'DB_NAME': "test_db",
        'DB_USER': "test_user",
        'DB_PASSWORD': "test_password"
    })

    # Mock database connection and cursor
    mock_conn = mocker.patch('psycopg2.connect')
    mock_cursor = mock_conn.return_value.__enter__.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [('AAPL',), ('GOOGL',)]

    # Mock yfinance's Ticker and its history method
    mock_ticker = mock_yfinance
    mock_stock = mock_ticker.return_value
    mock_stock.history.return_value = pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-08'],
        'Close': [150, 160]
    })

    mock_to_csv = mocker.patch('get_stock_data.pd.DataFrame.to_csv')

    main()
    print(mock_ticker.mock_calls)
    mock_ticker.assert_any_call('GOOGL')
    mock_ticker.assert_any_call('AAPL')

    assert mock_to_csv.call_count == 2
