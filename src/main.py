"""
Точка входа в проект Transaction_analysis.
Позволяет запускать различные функции проекта из командной строки.
"""

import argparse
import json
import logging
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

# Настройка логирования для main
logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from src.reports import spending_by_weekday
from src.services import investment_bank_from_df

# Импорты из нашего проекта
from src.utils import load_transactions
from src.views import main_page

load_dotenv()


def run_main_page(date_time_str: str, data_file: str):
    """Запуск функциональности 'Главная'."""
    logger.info(f"Запуск 'Главная' для даты/времени: {date_time_str}")
    try:
        df = load_transactions(data_file)
        result = main_page(date_time_str, df)
        print("\n--- Результат 'Главная' ---")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("---------------------------")
    except Exception as e:
        logger.error(f"Ошибка при запуске 'Главная': {e}")
        print(f"Ошибка: {e}")


def run_investment_bank(target_date: str, limit: int, data_file: str):
    """Запуск функциональности 'Инвесткопилка'."""
    logger.info(f"Запуск 'Инвесткопилка' для даты: {target_date}, лимит: {limit}")
    try:
        df = load_transactions(data_file)
        saved_amount = investment_bank_from_df(target_date, df, limit)
        print("\n--- Результат 'Инвесткопилка' ---")
        print(f"Отложено в инвесткопилку: {saved_amount} RUB")
        print("---------------------------------")
    except Exception as e:
        logger.error(f"Ошибка при запуске 'Инвесткопилка': {e}")
        print(f"Ошибка: {e}")


def run_spending_report(target_date: str, data_file: str):
    """Запуск функциональности 'Траты по дням недели'."""
    logger.info(f"Запуск 'Траты по дням недели' для даты: {target_date}")
    try:
        df = load_transactions(data_file)
        result_df = spending_by_weekday(df, target_date)
        print("\n--- Результат 'Траты по дням недели' ---")
        if result_df.empty:
            print("Нет данных для отчета.")
        else:
            # Выводим в читаемом виде
            for _, row in result_df.iterrows():
                print(f"{row['weekday']:<9}: {row['average_spent']:>8.2f} RUB")
        print("----------------------------------------")
    except Exception as e:
        logger.error(f"Ошибка при запуске 'Траты по дням недели': {e}")
        print(f"Ошибка: {e}")


def main():
    """Главная функция для парсинга аргументов и запуска команд."""
    parser = argparse.ArgumentParser(description="Transaction Analysis Project")
    parser.add_argument(
        "--data-file",
        "-f",
        type=str,
        default=None,  # Путь по умолчанию будет в load_transactions
        help="Путь к файлу Excel с транзакциями (по умолчанию: ../data/operations.xlsx)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    # Подкоманда для "Главная"
    parser_main = subparsers.add_parser("main", help='Страница "Главная"')
    parser_main.add_argument("datetime", type=str, help="Дата и время в формате YYYY-MM-DD HH:MM:SS")

    # Подкоманда для "Инвесткопилка"
    parser_ib = subparsers.add_parser("investbank", help='Сервис "Инвесткопилка"')
    parser_ib.add_argument("date", type=str, help="Дата в формате YYYY-MM-DD для определения месяца расчета")
    parser_ib.add_argument(
        "--limit",
        "-l",
        type=int,
        choices=[10, 50, 100],
        default=50,
        help="Предел округления (10, 50, 100). По умолчанию: 50",
    )

    # Подкоманда для "Траты по дням недели"
    parser_report = subparsers.add_parser("report", help='Отчет "Траты по дням недели"')
    parser_report.add_argument(
        "--date",
        "-d",
        type=str,
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Дата в формате YYYY-MM-DD (по умолчанию: сегодня)",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    # Выбор и запуск команды
    if args.command == "main":
        run_main_page(args.datetime, args.data_file)
    elif args.command == "investbank":
        run_investment_bank(args.date, args.limit, args.data_file)
    elif args.command == "report":
        run_spending_report(args.date, args.data_file)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
