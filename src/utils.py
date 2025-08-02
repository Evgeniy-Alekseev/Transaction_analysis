import pandas as pd
from datetime import datetime, timedelta
import json
import logging
import requests
from typing import List, Dict, Any, Optional
import os

logger = logging.getLogger(__name__)


def load_transactions(file_path: str) -> pd.DataFrame:
    """Загружает транзакции из Excel файла."""
    logger.info(f"Загрузка транзакций из {file_path}")
    df = pd.read_excel(file_path)
    # Удаление строк с заголовками, если они повторяются
    df = df[df['Дата операции'] != 'Дата операции']
    # Преобразование дат
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], format='%d.%m.%Y %H:%M:%S', errors='coerce')
    df['Дата платежа'] = pd.to_datetime(df['Дата платежа'], format='%d.%m.%Y', errors='coerce')
    # Преобразование сумм в числа
    for col in ['Сумма операции', 'Сумма платежа', 'Кэшбэк', 'Бонусы (включая кэшбэк)', 'Округление на инвесткопилку',
                'Сумма операции с округлением']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    logger.info(f"Загружено {len(df)} транзакций")
    return df


def filter_transactions_by_date(df: pd.DataFrame, end_date: datetime) -> pd.DataFrame:
    """Фильтрует транзакции с начала месяца до end_date."""
    start_of_month = end_date.replace(day=1)
    logger.info(f"Фильтрация транзакций с {start_of_month.strftime('%Y-%m-%d')} по {end_date.strftime('%Y-%m-%d')}")
    mask = (df['Дата операции'] >= start_of_month) & (df['Дата операции'] <= end_date)
    return df.loc[mask].copy()


def get_greeting(hour: int) -> str:
    """Определяет приветствие по времени суток."""
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def load_user_settings(settings_path: str = "user_settings.json") -> Dict[str, Any]:
    """Загружает пользовательские настройки."""
    if not os.path.exists(settings_path):
        logger.warning(f"Файл настроек {settings_path} не найден. Используются значения по умолчанию.")
        return {"user_currencies": [], "user_stocks": []}
    with open(settings_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """Получает курс валют с API (например, exchangerate-api.com)."""
    rates = []
    if not currencies:
        return rates
    try:
        # Используем бесплатный API для примера
        url = "https://api.exchangerate-api.com/v4/latest/RUB"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        rub_rates = data.get("rates", {})
        for curr in currencies:
            rate = rub_rates.get(curr, None)
            rates.append({"currency": curr, "rate": rate})
    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {e}")
        # Возвращаем пустые значения в случае ошибки
        for curr in currencies:
            rates.append({"currency": curr, "rate": None})
    return rates


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """Получает цены на акции с API (например, alphavantage)."""
    prices = []
    if not stocks:
        return prices
    try:
        # Alpha Vantage требует API ключ, для демонстрации используем mock данные
        # url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
        # response = requests.get(url)
        # data = response.json()
        # price = data.get("Global Quote", {}).get("05. price", None)
        # Для упрощения, используем мок
        for stock in stocks:
            prices.append({"stock": stock, "price": "N/A (API Key Required)"})
    except Exception as e:
        logger.error(f"Ошибка при получении цен на акции: {e}")
        for stock in stocks:
            prices.append({"stock": stock, "price": None})
    return prices


def calculate_card_stats(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Рассчитывает статистику по картам."""
    cards_data = []
    # Фильтруем только расходы (отрицательные суммы)
    expenses_df = df[df['Сумма операции'] < 0].copy()

    if 'Номер карты' not in expenses_df.columns:
        logger.warning("Столбец 'Номер карты' не найден в данных.")
        return cards_data

    for card_number in expenses_df['Номер карты'].dropna().unique():
        card_df = expenses_df[expenses_df['Номер карты'] == card_number]

        last_digits = card_number[-4:] if isinstance(card_number, str) else "N/A"

        total_spent = abs(card_df['Сумма операции'].sum())

        # Кэшбэк: 1 рубль на каждые 100 рублей
        cashback = total_spent // 100

        # Топ-5 транзакций по сумме платежа (по модулю)
        top_transactions = card_df.nlargest(5, 'Сумма платежа', key=abs)[
            ['Дата операции', 'Сумма платежа', 'Категория', 'Описание']].to_dict('records')
        # Форматируем дату для JSON
        for t in top_transactions:
            t['Дата операции'] = t['Дата операции'].strftime('%d.%m.%Y %H:%M:%S') if pd.notna(
                t['Дата операции']) else None

        cards_data.append({
            "last_digits": last_digits,
            "total_spent": round(total_spent, 2),
            "cashback": cashback,
            "top_transactions": top_transactions
        })
    return cards_data
