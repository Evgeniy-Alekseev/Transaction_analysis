import functools
import json
import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


def report_to_file(filename: Optional[str] = None):
    """Декоратор для записи результата отчета в файл."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result_df = func(*args, **kwargs)
            if result_df is not None and not result_df.empty:
                output_filename = filename or f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                # Преобразуем DataFrame в JSON
                result_json = result_df.to_dict(orient="records")
                with open(output_filename, "w", encoding="utf-8") as f:
                    json.dump(result_json, f, ensure_ascii=False, indent=4)
                logger.info(f"Отчет сохранен в файл: {output_filename}")
            else:
                logger.warning("Отчет пустой, файл не создан.")
            return result_df

        return wrapper

    return decorator


@report_to_file()  # Можно использовать как @report_to_file("my_report.json")
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает средние траты по дням недели за последние 3 месяца от указанной даты.
    """
    logger.info(f"Генерация отчета 'Траты по дням недели' для даты {date}")

    if date:
        try:
            end_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            logger.error(f"Неверный формат даты: {date}")
            raise ValueError("Дата должна быть в формате YYYY-MM-DD")
    else:
        end_date = datetime.now()

    start_date = end_date - timedelta(days=90)  # Примерно 3 месяца

    # Фильтруем транзакции
    mask = (
        (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= end_date)
        & (transactions["Сумма операции"] < 0)
    )
    filtered_df = transactions.loc[mask].copy()

    if filtered_df.empty:
        logger.warning("Нет данных для отчета за указанный период.")
        return pd.DataFrame()

    # Добавляем день недели
    filtered_df["weekday"] = filtered_df["Дата операции"].dt.day_name()

    # Группируем по дню недели и считаем среднее
    avg_spending = filtered_df.groupby("weekday")["Сумма операции"].mean().abs().reset_index()
    avg_spending.rename(columns={"Сумма операции": "average_spent"}, inplace=True)

    # Сортируем по дням недели
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    avg_spending["weekday"] = pd.Categorical(avg_spending["weekday"], categories=day_order, ordered=True)
    avg_spending.sort_values("weekday", inplace=True)
    avg_spending["weekday"] = avg_spending["weekday"].astype(str)  # Для сериализации

    logger.info("Отчет 'Траты по дням недели' сгенерирован.")
    return avg_spending
