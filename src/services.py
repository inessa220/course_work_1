import json
import re
from typing import Any, Dict, Hashable, List

from src.logg import services_logger


def search_by_word(transactions: List[Dict[Hashable, Any]], search_words: str) -> str:
    """Функция реализует простой поиск по указанным словам в описании."""
    try:
        filtered_data = filter(
            lambda item: re.findall(search_words, item.get("Описание", ""), flags=re.I), transactions
        )
        return json.dumps(list(filtered_data), ensure_ascii=False, indent=4)
    except Exception as e:
        services_logger.error(f"Ошибка при поиске транзакций: {e}")
        return "[]"


def search_by_phone(transactions: List[Dict[Hashable, Any]]) -> str:
    """Функция возвращает транзации, содержащие телефонные номера в описании."""
    try:
        pattern = r"\+7\s?\d{3}\s?\d{2}-\d{2}-\d{2}"
        filtered_data = filter(lambda item: re.search(pattern, item.get("Описание", "")), transactions)
        return json.dumps(list(filtered_data), ensure_ascii=False, indent=4)
    except Exception as e:
        services_logger.error(f"Ошибка при поиске номеров телефонов: {e}")
        return "[]"


def search_by_client_name(transactions: List[Dict[Hashable, Any]]) -> str:
    """Функция возвращает транзации, содержащие имя и первую букву фамилии в описании."""
    try:
        pattern = r"\b[А-ЯЁ][а-яё]+\s[А-Я]\."
        filtered_data = filter(lambda item: re.search(pattern, item.get("Описание", "")), transactions)
        return json.dumps(list(filtered_data), ensure_ascii=False, indent=4)
    except Exception as e:
        services_logger.error(f"Ошибка при поиске имен клиентов: {e}")
        return "[]"
