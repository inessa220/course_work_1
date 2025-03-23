import json
import os
import re
from datetime import date
from typing import Any, Dict, Hashable, List, Optional

import pandas as pd

from src.api import get_currency_rate, get_stock_price
from src.logg import views_logger
from src.utils import get_date_interval, get_greeting, read_file

base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "..", "user_settings.json")

with open(file_path, "r", encoding="utf-8") as f:
    user_settings = json.load(f)


def get_card_number(card_number: str) -> str:
    """Функция извлекает последние 4 цифры номера карты."""
    try:
        card_clean = re.findall(r"\d+", str(card_number))
        return card_clean[0][-4:] if card_clean else "Нет информации о карте"
    except TypeError:
        views_logger.error("Ошибка: неверный формат номера карты")


def get_filtered_transactions(transactions: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    """Функция фильтрует транзакции по заданному диапазону дат"""
    try:
        if transactions.empty:
            views_logger.warning("Передан пустой DataFrame с транзакциями.")
            return pd.DataFrame()
        transactions = transactions.copy()
        transactions["Дата платежа_dt"] = pd.to_datetime(transactions["Дата платежа"], dayfirst=True, errors="coerce")
        transactions = transactions.dropna(subset=["Дата платежа_dt"])
        transactions = transactions[
            (transactions["Дата платежа_dt"] >= start) & (transactions["Дата платежа_dt"] <= end)
        ]
        transactions["Номер карты"] = transactions["Номер карты"].fillna("Нет информации о карте")
        return transactions
    except KeyError as e:
        views_logger.error(f"Ошибка: отсутствует столбец {e}")
    except ValueError as e:
        views_logger.error(f"Ошибка обработки даты: {e}")
    return pd.DataFrame()


def get_transaction_exchange(transactions: pd.DataFrame) -> pd.DataFrame:
    """Функция конвертирует суммы платежей в рубли по текущему курсу валют."""
    try:
        if transactions.empty:
            views_logger.warning("Передан пустой DataFrame для конвертации.")
            return transactions
        currencies = transactions["Валюта платежа"].unique()
        currency_map = {currency: get_currency_rate(currency) if currency != "RUB" else 1 for currency in currencies}
        transactions = transactions.copy()
        transactions["exchange_rate"] = transactions["Валюта платежа"].map(currency_map)
        transactions["Сумма платежа_ex"] = transactions["Сумма платежа"] / transactions["exchange_rate"]
        return transactions
    except KeyError:
        views_logger.error("Ошибка: отсутствует столбец 'Валюта платежа' или 'Сумма платежа'.")
    return transactions


def get_card_sum_cashback(transactions: pd.DataFrame, card_number: Optional[str]) -> (float, float):
    """Вычисляет сумму расходов и начисленный кэшбэк по указанной карте."""
    try:
        if transactions.empty:
            return 0.0, 0.0
        if card_number:
            transactions = transactions[transactions["Номер карты"] == card_number]
        transactions_sum = round(transactions["Сумма платежа_ex"].sum(), 2)
        transactions_cashback = round(transactions_sum / 100, 2)
        return float(transactions_sum), float(transactions_cashback)
    except KeyError:
        views_logger.error("Ошибка: отсутствует столбец 'Номер карты' или 'Сумма платежа_ex'.")
    return 0.0, 0.0


def get_cards_info(transactions: pd.DataFrame) -> List[Dict[Hashable, Any]]:
    """Функция собирает информацию по картам: сумма расходов и начисленный кэшбэк."""
    try:
        if transactions.empty:
            return []
        cards_info = []
        cards_numbers = transactions["Номер карты"].dropna().unique()
        for card_number in cards_numbers:
            last_digits = get_card_number(card_number)
            total_spent, cashback = get_card_sum_cashback(transactions, card_number)
            cards_info.append({"last_digits": last_digits, "total_spent": total_spent, "cashback": cashback})
        return cards_info
    except KeyError:
        views_logger.error("Ошибка: отсутствует столбец 'Номер карты'.")
    return []


def get_top_5_transactions(transactions: pd.DataFrame) -> List[Dict[Hashable, Any]]:
    """Функция получает топ-5 транзаций по сумме платежа."""
    try:
        if transactions.empty:
            return []
        transaction_cols = ["Дата платежа", "Сумма платежа_ex", "Категория", "Описание"]
        transaction_cols_json = ["date", "amount", "category", "description"]
        transaction_cols_map = dict(zip(transaction_cols, transaction_cols_json))
        top_transactions = transactions.sort_values(by="Сумма платежа_ex", ascending=False).head(5)
        top_transactions = top_transactions[transaction_cols].rename(columns=transaction_cols_map)
        return top_transactions.to_dict(orient="records")
    except KeyError as e:
        views_logger.error(f"Ошибка: отсутствует столбец {e}")
    except ValueError as e:
        views_logger.error(f"Ошибка обработки данных: {e}")
    return []


def get_exchange_stock(result: Dict[Hashable, Any]) -> Dict[Hashable, Any]:
    """Функция получает информацию о курсе валют и стоимости акций"""
    result["currency_rates"] = [
        {currency: get_currency_rate(currency)} for currency in user_settings["user_currencies"]
    ]
    result["stock_prices"] = [
        {"stock": stock, "price": get_stock_price(stock)} for stock in user_settings["user_stocks"]
    ]
    return result


def main_page(input_date: str) -> str:
    """Функция страницы "Главная" """
    result = dict()

    # Добавляем приветствие
    result["greeting"] = get_greeting()

    # Читаем и фильтруем данные
    transactions = read_file("operations.xlsx")
    start, end = get_date_interval(input_date)
    transactions = get_filtered_transactions(transactions, start, end)

    if transactions.empty:
        result["cards"] = []
        result["top_transactions"] = []
        result["currency_rates"] = [
            {currency: get_currency_rate(currency)} for currency in user_settings["user_currencies"]
        ]
        result["stock_prices"] = [{stock: get_stock_price(stock)} for stock in user_settings["user_stocks"]]
        return ""

    # Расходы
    expenses = transactions[transactions["Сумма платежа"] < 0].copy()
    expenses["Сумма платежа"] = expenses["Сумма платежа"].abs()
    expenses = get_transaction_exchange(expenses)

    # Информация о картах
    result["cards"] = get_cards_info(expenses)

    # Информация о топ-5 транзакциях
    result["top_transactions"] = get_top_5_transactions(expenses)

    # Информация о курсах валют и акциях
    result = get_exchange_stock(result)

    return json.dumps(result, ensure_ascii=False, indent=2)
