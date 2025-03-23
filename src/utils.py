import os
from datetime import date, datetime
from typing import Tuple
import pandas as pd
from src.logg import utils_logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = "data"


def read_file(filename: str) -> pd.DataFrame:
    """Функция чтения файла Excel"""
    try:
        filepath = os.path.join(BASE_DIR, DATA_FOLDER, filename)
        transactions = pd.read_excel(filepath)
        if transactions.empty:
            utils_logger.error(f"Файл {filename} c транзакциями пуст.")
            return pd.DataFrame()
        return transactions
    except FileNotFoundError:
        utils_logger.error(f"Файл {filename} не найден.")
        return pd.DataFrame()
    except (TypeError, ValueError, pd.errors.ParserError) as e:
        utils_logger.error(f"Ошибка обработки данных в файле {filename}: {e}")
        return pd.DataFrame()
    return pd.DataFrame()


def get_greeting() -> str:
    """Функция приветствия в зависимости от времени суток."""
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_date_interval(input_date: str) -> Tuple[date, date]:
    """Функция возвращает первую дату текущего месяца и сегодняшнюю дату."""
    if not isinstance(input_date, str):
        raise ValueError("Дата должна быть строкой")
    if not input_date.strip():
        raise ValueError("Дата не может быть пустой")
    try:
        end = datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")
        start = end.replace(day=1)
    except ValueError:
        raise ValueError("Некорректный формат даты")
    return start, end
