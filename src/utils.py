import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_transactions(file_path: Optional[str] = None) -> pd.DataFrame:
    """
    Загружает транзакции из Excel файла.
    Если путь не указан, пытается загрузить из стандартного местоположения.
    """
    if file_path is None:
        # Предполагаем, что файл лежит в ../data/operations.xlsx относительно src/
        # Требуется для main.py при запуске из корня проекта как python -m src.main
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "operations.xlsx")
        logger.info(f"Путь к файлу транзакций не указан. Используется путь по умолчанию: {file_path}")

    if not os.path.exists(file_path):
        logger.error(f"Файл транзакций не найден: {file_path}")
        raise FileNotFoundError(f"Файл транзакций не найден: {file_path}")

    logger.info(f"Загрузка транзакций из {file_path}")
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        logger.error(f"Ошибка при чтении Excel файла: {e}")
        raise

    # Преобразование дат
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
    df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], format="%d.%m.%Y", errors="coerce")

    # Преобразование сумм в числа
    for col in [
        "Сумма операции",
        "Сумма платежа",
        "Кэшбэк",
        "Бонусы (включая кэшбэк)",
        "Округление на инвесткопилку",
        "Сумма операции с округлением",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    logger.info(f"Загружено {len(df)} транзакций")
    return df


def filter_transactions_by_date(df: pd.DataFrame, end_date: datetime) -> pd.DataFrame:
    """Фильтрует транзакции с начала месяца до end_date."""
    start_of_month = end_date.replace(day=1)
    logger.info(f"Фильтрация транзакций с {start_of_month.strftime('%Y-%m-%d')} по {end_date.strftime('%Y-%m-%d')}")
    mask = (df["Дата операции"] >= start_of_month) & (df["Дата операции"] <= end_date)
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
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON в файле {settings_path}: {e}")
        return {"user_currencies": [], "user_stocks": []}


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """Получает курс валют с API."""
    rates = []
    if not currencies:
        return rates

    api_key = os.getenv("CURRENCY_API_KEY")
    if not api_key:
        logger.error("API-ключ CURRENCY_API_KEY не найден в переменных окружения.")
        for curr in currencies:
            rates.append({"currency": curr, "rate": None})
        return rates

    try:
        # Исправленный URL
        url = "https://api.apilayer.com/exchangerates_data/latest"
        headers = {"apikey": api_key}
        params = {"base": "RUB", "symbols": ",".join(currencies)}

        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("success") is False:
            error_info = data.get("error", {}).get("info", "Неизвестная ошибка API")
            logger.error(f"Ошибка API exchangerates_ {error_info}")
            raise requests.exceptions.RequestException(error_info)

        rub_rates = data.get("rates", {})
        for curr in currencies:
            rate = rub_rates.get(curr, None)
            rates.append({"currency": curr, "rate": rate})

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка сети или запроса к API exchangerates_ {e}")
        for curr in currencies:
            rates.append({"currency": curr, "rate": None})
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON ответа от API: {e}")
        for curr in currencies:
            rates.append({"currency": curr, "rate": None})
    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {e}")
        for curr in currencies:
            rates.append({"currency": curr, "rate": None})
    return rates


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """
    Получает цены на акции из API-Ninjas S&P 500.
    """
    prices = []
    if not stocks:
        return prices

    api_key = os.getenv("STOCKS_API_KEY")
    if not api_key:
        logger.error("API-ключ STOCKS_API_KEY не найден в переменных окружения.")
        for stock in stocks:
            prices.append({"stock": stock, "price": None})
        return prices

    try:
        url = "https://api.api-ninjas.com/v1/sp500"
        headers = {"X-Api-Key": api_key}

        logger.debug(f"Запрос списка компаний S&P 500 по адресу: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        all_sp500_data = response.json()

        sp500_prices_dict = {item["symbol"]: item["price"] for item in all_sp500_data}

        for stock_symbol in stocks:
            price = sp500_prices_dict.get(stock_symbol)
            if price is not None:
                prices.append({"stock": stock_symbol, "price": price})
                logger.debug(f"Цена для {stock_symbol}: {price}")
            else:
                prices.append({"stock": stock_symbol, "price": None})
                logger.warning(f"Цена для акции {stock_symbol} не найдена в данных S&P 500.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка сети или запроса к API-Ninjas S&P 500: {e}")
        for stock in stocks:
            prices.append({"stock": stock, "price": None})
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON ответа от API-Ninjas: {e}")
        for stock in stocks:
            prices.append({"stock": stock, "price": None})
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении цен на акции: {e}")
        for stock in stocks:
            prices.append({"stock": stock, "price": None})

    return prices


def calculate_card_stats(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Рассчитывает статистику по картам."""
    cards_data = []
    expenses_df = df[df["Сумма операции"] < 0].copy()

    if "Номер карты" not in expenses_df.columns or expenses_df["Номер карты"].isna().all():
        logger.warning("Столбец 'Номер карты' не найден в данных или все значения NaN.")
        return cards_data

    for card_number in expenses_df["Номер карты"].dropna().unique():
        card_df = expenses_df[expenses_df["Номер карты"] == card_number]

        # Убедимся, что card_number - строка
        card_number_str = str(card_number)
        last_digits = card_number_str[-4:] if len(card_number_str) >= 4 else card_number_str

        total_spent = abs(card_df["Сумма операции"].sum())
        cashback = total_spent // 100

        # Используем nlargest с временным столбцом для совместимости
        card_df_copy = card_df.copy()
        card_df_copy["Abs_Summa_platezha"] = card_df_copy["Сумма платежа"].abs()
        top_transactions_df = card_df_copy.nlargest(5, "Abs_Summa_platezha")
        top_transactions = top_transactions_df[
            ["Дата операции", "Сумма платежа", "Категория", "Описание"]
        ].to_dict("records")
        # Форматируем дату
        for t in top_transactions:
            t["Дата операции"] = (
                t["Дата операции"].strftime("%d.%m.%Y %H:%M:%S") if pd.notna(t["Дата операции"]) else None
            )

        cards_data.append(
            {
                "last_digits": last_digits,
                "total_spent": round(total_spent, 2),
                "cashback": int(cashback),
                "top_transactions": top_transactions,
            }
        )
    return cards_data
