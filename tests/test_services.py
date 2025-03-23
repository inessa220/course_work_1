import json

from src.services import (search_by_client_name, search_by_phone, search_by_word)


def test_search_by_word(search_word_fixture):
    result = search_by_word(search_word_fixture, "метро")
    expected = '[{"Описание": "Метро Санкт-Петербург"}, {"Описание": "Метро Мск"}]'
    assert json.loads(result) == json.loads(expected)


def test_test_search_by_word_exception(search_word_fixture):
    result = search_by_word(search_word_fixture, "что-то")
    expected = "[]"
    assert json.loads(result) == json.loads(expected)


def test_search_by_phone(search_word_fixture):
    result = search_by_phone(search_word_fixture)
    expected = '[{"Описание": "Перевод +7 987 65-43-21"}]'
    assert json.loads(result) == json.loads(expected)


def test_search_by_phone_exception():
    result = search_by_phone([])
    expected = "[]"
    assert json.loads(result) == json.loads(expected)


def test_search_by_client_name(search_word_fixture):
    result = search_by_client_name(search_word_fixture)
    expected = '[{"Описание": "Оплата Василий П."}, {"Описание": "Оплата Петр В."}]'
    assert json.loads(result) == json.loads(expected)


def test_search_by_client_name_exception():
    result = search_by_client_name([])
    expected = "[]"
    assert json.loads(result) == json.loads(expected)
