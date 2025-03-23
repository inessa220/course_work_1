from unittest.mock import patch

import pytest

from src.api import get_currency_rate, get_stock_price


@patch("src.api.requests.get")
def test_get_currency_rate(mocked_get):
    mocked_get.return_value.status_code = 200
    mocked_get.return_value.json.return_value = {"rates": {"RUB": 100.0}}
    expected_value = 100.0

    assert get_currency_rate(base="RUB") == expected_value
    mocked_get.assert_called_once()


@patch("src.api.requests.get")
def test_get_currency_key_error(mocked_get):
    mocked_get.return_value.status_code = 200
    mocked_get.return_value.json.return_value = {}
    with pytest.raises(ValueError, match="Ошибка в данных API: нет ключа 'rate'"):
        get_currency_rate(base="RUB")


@patch("src.api.get_currency_rate")
@patch("src.api.yf.Ticker")
def test_get_stock_prices_fast_info(mock_ticker, mock_currency):
    mock_currency.return_value = 100
    mock_ticker.return_value.fast_info = {"last_price": 150}
    mock_ticker.return_value.info = {"currency": "USD"}

    result = get_stock_price("AAPL")
    assert result == 1.5


@patch("src.api.yf.Ticker")
def test_get_stock_prices_current_price(mock_ticker):
    mock_ticker.return_value.info = {"currency": "RUB", "currentPrice": 150}

    result = get_stock_price("AAPL")
    assert result == 150


@patch("src.api.get_currency_rate")
@patch("src.api.yf.Ticker")
def test_get_stock_prices_undefined(mock_ticker, mock_currency):
    mock_currency.return_value = 100
    mock_ticker.return_value.fast_info = {}

    result = get_stock_price("AAPL")
    assert result is None
