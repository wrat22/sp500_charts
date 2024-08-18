import os
import sys
import time
import pytest
import pandas as pd

# Add the directory containing `app.py` to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, calculate_pct_change, calculate_last_week


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_data():
    data = {
        'ticker': ['AAPL', 'AAPL', 'AAPL'],
        'date': pd.to_datetime(['2023-07-01', '2023-07-08', '2023-07-15']),
        'close': [150, 155, 160]
    }
    return pd.DataFrame(data)


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'S&P500 Stocks Analysis' in response.data


def test_get_stock_data_valid(client, sample_data, mocker):
    mocker.patch('app.pandas_companies_df', pd.DataFrame({
        'ticker': ['AAPL', 'GOOGL'],
        'name': ['Apple', 'Google']
    }))
    mocker.patch('app.pandas_value_df', sample_data)

    response = client.post('/get_stock_data', data={'ticker': 'Apple'})
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'graph' in json_data
    assert 'pct_change' in json_data
    assert 'last_week_value' in json_data
    assert json_data['name'] == 'Apple'
    assert json_data['ticker'] == 'AAPL'


def test_get_stock_data_invalid_company(client, mocker):
    mocker.patch('app.pandas_companies_df', pd.DataFrame({
        'ticker': ['AAPL', 'GOOGL'],
        'name': ['Apple', 'Google']
    }))
    mocker.patch('app.pandas_value_df', pd.DataFrame())

    response = client.post('/get_stock_data', data={'ticker': 'InvalidCompany'})
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'error' in json_data
    assert json_data['error'] == 'Company name not found'


def test_get_stock_data_no_ticker_data(client, mocker):
    mocker.patch('app.pandas_companies_df', pd.DataFrame({
        'ticker': ['AAPL', 'GOOGL'],
        'name': ['Apple', 'Google']
    }))
    mocker.patch('app.pandas_value_df', pd.DataFrame({
        'ticker': [],
        'date': [],
        'close': []
    }))

    response = client.post('/get_stock_data', data={'ticker': 'Apple'})
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'error' in json_data
    assert json_data['error'] == 'Stock ticker not found'


def test_calculate_pct_change(sample_data):
    pct_change = calculate_pct_change(sample_data, 'AAPL')
    assert pct_change == pytest.approx(3.23, 0.01)


def test_calculate_last_week(sample_data):
    last_week_value = calculate_last_week(sample_data, 'AAPL')
    assert last_week_value == 160


def test_calculate_pct_change_empty():
    df = pd.DataFrame(columns=['ticker', 'date', 'close'])
    with pytest.raises(IndexError):
        calculate_pct_change(df, 'AAPL')


def test_calculate_pct_change_single_row():
    df = pd.DataFrame({'ticker': 'AAPL', 'date': ['2023-07-15'], 'close': [150]})
    with pytest.raises(IndexError):
        calculate_pct_change(df, 'AAPL')


def test_calculate_last_week_empty():
    df = pd.DataFrame(columns=['ticker', 'date', 'close'])
    with pytest.raises(IndexError):
        calculate_last_week(df, 'AAPL')


def test_get_stock_data_invalid_ticker_format(client):
    response = client.post('/get_stock_data', data={'ticker': 12345})
    json_data = response.get_json()
    assert 'error' in json_data


def test_get_stock_data_long_ticker(client):
    response = client.post('/get_stock_data', data={'ticker': 'A'*256})
    json_data = response.get_json()
    assert 'error' in json_data


def test_json_structure(client, mocker, sample_data):
    mocker.patch('app.pandas_companies_df', pd.DataFrame({
        'ticker': ['AAPL', 'GOOGL'],
        'name': ['Apple', 'Google']
    }))
    mocker.patch('app.pandas_value_df', sample_data)

    response = client.post('get_stock_data', data={'ticker': 'Apple'})
    json_data = response.get_json()

    assert set(json_data.keys()) == {'graph', 'pct_change', 'name', 'ticker', 'last_week_value'}


def test_response_time(client):
    start_time = time.time()
    response = client.get('/')
    end_time = time.time()

    assert response.status_code == 200

    assert (end_time - start_time) < 1