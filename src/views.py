import logging
from datetime import datetime

import pandas as pd

from src.utils import (calculate_card_stats, filter_transactions_by_date, get_currency_rates, get_greeting,
                       get_stock_prices, load_user_settings)

logger = logging.getLogger(__name__)


def main_page(date_time_str: str, df: pd.DataFrame) -> dict:
    """
    Функция для веб-страницы "Главная".
    Принимает строку с датой и временем и DataFrame с транзакциями.
    Возвращает JSON-ответ.
    """
    logger.info(f"Генерация главной страницы для {date_time_str}")
    try:
        target_datetime = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        logger.error(f"Неверный формат даты: {date_time_str}")
        raise ValueError("Дата должна быть в формате YYYY-MM-DD HH:MM:SS") from e

    # 1. Фильтрация транзакций
    filtered_df = filter_transactions_by_date(df, target_datetime)

    # 2. Приветствие
    greeting = get_greeting(target_datetime.hour)

    # 3. Настройки пользователя
    settings = load_user_settings()
    currencies = settings.get("user_currencies", [])
    stocks = settings.get("user_stocks", [])

    # 4. Статистика по картам
    cards = calculate_card_stats(filtered_df)

    # 5. Курсы валют
    currency_rates = get_currency_rates(currencies)

    # 6. Цены на акции
    stock_prices = get_stock_prices(stocks)

    response = {"greeting": greeting, "cards": cards, "currency_rates": currency_rates, "stock_prices": stock_prices}

    logger.info("Главная страница сгенерирована успешно.")
    return response
