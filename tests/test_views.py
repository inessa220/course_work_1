from unittest.mock import patch

import pandas as pd

from src.views import (get_card_number, get_card_sum_cashback, get_cards_info, get_exchange_stock,
                       get_filtered_transactions, get_top_5_transactions, get_transaction_exchange)


def test_get_card_number():
    assert get_card_number("*5678") == "5678"
    assert get_card_number("9876") == "9876"
    assert get_card_number("") == "Нет информации о карте"
    assert get_card_number("abcd") == "Нет информации о карте"


def test_get_filtered_transactions(filtered_transactions_fixture):
    transactions, start_date, end_date, expected_result = filtered_transactions_fixture
    transactions = pd.DataFrame(transactions)
    filtered = get_filtered_transactions(transactions, start_date, end_date)
    assert len(filtered) == expected_result


@patch("src.views.get_currency_rate", side_effect=lambda x: 10 if x == "CNY" else 1)
def test_get_transaction_exchange(mock_get_currency_rate, transactions):
    transactions = pd.DataFrame(transactions).head(2)
    exchanged = get_transaction_exchange(transactions)

    assert "Сумма платежа_ex" in exchanged.columns
    assert float(exchanged.loc[exchanged["Валюта платежа"] == "RUB", "Сумма платежа_ex"].iloc[0]) == -160.89
    assert float(exchanged.loc[exchanged["Валюта платежа"] == "CNY", "Сумма платежа_ex"].iloc[0]) == -10


@patch("src.views.get_currency_rate", side_effect=lambda x: 10 if x == "CNY" else 1)
def test_get_transaction_exchange_error(mock_get_currency_rate, transaction_exchange_error_fixture):
    transactions = pd.DataFrame(transaction_exchange_error_fixture)
    exchanged = get_transaction_exchange(transactions)
    assert len(exchanged) == 2


def test_get_card_sum_cashback(transactions):
    transactions = pd.DataFrame(transactions)
    transactions["Сумма платежа_ex"] = transactions["Сумма платежа"]
    total, cashback = get_card_sum_cashback(transactions, None)
    assert total == sum(transactions["Сумма платежа"])
    assert cashback == round(total / 100, 2)


def test_get_card_sum_cashback_error(card_sum_cashback_fixture):
    transactions, card_number, exp_total, exp_cashback = card_sum_cashback_fixture
    transactions = pd.DataFrame(transactions)
    total, cashback = get_card_sum_cashback(transactions, card_number)
    assert total == exp_total
    assert cashback == exp_cashback


def test_get_cards_info(transactions):
    transactions = pd.DataFrame(transactions)
    transactions["Сумма платежа_ex"] = transactions["Сумма платежа"]
    cards_info = get_cards_info(transactions)
    assert len(cards_info) == 2
    assert cards_info[0]["last_digits"] == "7197"


def test_get_top_5_transactions(transactions):
    transactions = pd.DataFrame(transactions)
    transactions["Сумма платежа_ex"] = transactions["Сумма платежа"].abs()
    top_5 = get_top_5_transactions(transactions)
    assert len(top_5) == 5
    assert top_5[0]["amount"] == 160.89


def test_get_top_5_transactions_key_error(transactions):
    transactions = pd.DataFrame(transactions)
    top_5 = get_top_5_transactions(transactions)
    assert top_5 == []


@patch("src.views.get_currency_rate")
@patch("src.views.get_stock_price")
def test_get_exchange_stock(mock_get_stock, mock_get_currency):
    mock_get_currency.side_effect = lambda x: 90.0 if x == "USD" else 98.5
    mock_get_stock.side_effect = lambda x: 150.0 if x == "AAPL" else 2800.0 if x == "GOOGL" else 700.0

    result = get_exchange_stock({})

    expected_currencies = [{"USD": 90.0}, {"EUR": 98.5}]

    assert result["currency_rates"] == expected_currencies
    assert any(stock["stock"] == "AAPL" for stock in result["stock_prices"])
    assert any(stock["stock"] == "GOOGL" for stock in result["stock_prices"])
