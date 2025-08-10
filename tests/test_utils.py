import pandas as pd
import pytest
from datetime import datetime
from src.utils import (
    filter_transactions_by_date,
    get_greeting,
    load_user_settings,
    get_currency_rates,
    get_stock_prices,
    calculate_card_stats,
)
from unittest.mock import patch, MagicMock
import os


def test_filter_transactions_by_date(sample_transactions_df):
    # Тестовая дата: 25.10.2021
    target_date = datetime(2021, 10, 25, 15, 0, 0)
    # Ожидаем, что попадут транзакции от 01.10.2021 до 25.10.2021
    # В sample_transactions_df есть 4 транзакции, все от 24 и 25 октября.
    filtered_df = filter_transactions_by_date(sample_transactions_df, target_date)
    # Проверим, что все 4 транзакции попали
    assert len(filtered_df) == 4
    # Проверим, что даты в диапазоне
    assert all(filtered_df['Дата операции'] >= datetime(2021, 10, 1))
    assert all(filtered_df['Дата операции'] <= target_date)


def test_get_greeting():
    assert get_greeting(6) == "Доброе утро"
    assert get_greeting(12) == "Добрый день"
    assert get_greeting(18) == "Добрый вечер"
    assert get_greeting(23) == "Доброй ночи"
    assert get_greeting(5) == "Доброй ночи"  # Граничное значение


def test_load_user_settings_default(monkeypatch, tmp_path):
    # Создаем временную директорию без файла настроек
    monkeypatch.chdir(tmp_path)
    # Убеждаемся, что файла нет
    if os.path.exists("user_settings.json"):
        os.remove("user_settings.json")

    settings = load_user_settings()
    assert settings == {"user_currencies": [], "user_stocks": []}


def test_load_user_settings_custom(temp_user_settings_file):
    settings = load_user_settings(temp_user_settings_file)
    assert "user_currencies" in settings
    assert "USD" in settings["user_currencies"]
    assert "user_stocks" in settings
    assert "AAPL" in settings["user_stocks"]


@patch('src.utils.requests.get')
def test_get_currency_rates_success(mock_get, mock_api_responses):
    mock_get.return_value = mock_api_responses["currency"]
    rates = get_currency_rates(["USD", "EUR"])
    assert len(rates) == 2
    assert rates[0]["currency"] == "USD"
    assert rates[0]["rate"] == 75.0
    assert rates[1]["currency"] == "EUR"
    assert rates[1]["rate"] == 85.0


@patch('src.utils.requests.get')
def test_get_currency_rates_failure(mock_get):
    mock_get.side_effect = Exception("API Error")
    rates = get_currency_rates(["USD"])
    assert len(rates) == 1
    assert rates[0]["currency"] == "USD"
    assert rates[0]["rate"] is None


# get_stock_prices сложно полноценно протестировать без ключа API,
# но можно проверить, что она не падает и возвращает список.
def test_get_stock_prices():
    prices = get_stock_prices(["AAPL"])
    assert isinstance(prices, list)
    # В текущей реализации возвращается заглушка
    assert len(prices) == 1
    assert prices[0]["stock"] == "AAPL"


def test_calculate_card_stats(sample_transactions_df):
    stats = calculate_card_stats(sample_transactions_df)
    assert len(stats) == 1  # Одна карта
    card_stat = stats[0]
    assert card_stat["last_digits"] == "7197"
    # Общая сумма: 135.47 + 273.90 + 129.00 + 4.94 = 543.31
    assert card_stat["total_spent"] == 543.31
    # Кэшбэк: 543.31 // 100 = 5
    assert card_stat["cashback"] == 5
    # Топ-5 транзакций (в данном случае все 4)
    assert len(card_stat["top_transactions"]) == 4
    # Проверим, что транзакции отсортированы по сумме (по модулю)
    top_amounts = [abs(t['Сумма платежа']) for t in card_stat["top_transactions"]]
    assert top_amounts == sorted(top_amounts, reverse=True)


def test_calculate_card_stats_no_cards(sample_transactions_df):
    empty_df = pd.DataFrame(columns=sample_transactions_df.columns)
    empty_df['Дата операции'] = pd.to_datetime(empty_df['Дата операции'], errors='coerce')
    empty_df['Дата платежа'] = pd.to_datetime(empty_df['Дата платежа'], errors='coerce')
    for col in ['Сумма операции', 'Сумма платежа', 'Кэшбэк', 'Бонусы (включая кэшбэк)', 'Округление на инвесткопилку', 'Сумма операции с округлением']:
        if col in empty_df.columns:
             empty_df[col] = pd.to_numeric(empty_df[col], errors='coerce')
    
    stats = calculate_card_stats(empty_df)
    assert stats == []

def test_calculate_card_stats_nan_cards(sample_transactions_df):
    df_with_nan = sample_transactions_df.copy()
    df_with_nan['Номер карты'] = None # Все значения NaN
    stats = calculate_card_stats(df_with_nan)
    assert stats == []
