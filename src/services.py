import logging
import math
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """
    Рассчитывает сумму, отложенную в инвесткопилку за указанный месяц.
    """
    logger.debug(f"Расчет инвесткопилки для месяца {month} с лимитом {limit}")

    if limit not in [10, 50, 100]:
        logger.warning(f"Некорректный лимит округления: {limit}. Используется 50.")
        limit = 50  # По заданию 50

    try:
        target_month_start = datetime.strptime(month, "%Y-%m")
        if target_month_start.month == 12:
            next_month_start = target_month_start.replace(year=target_month_start.year + 1, month=1)
        else:
            next_month_start = target_month_start.replace(month=target_month_start.month + 1)
    except ValueError as e:
        logger.error(f"Неверный формат месяца: {month}")
        raise ValueError("Месяц должен быть в формате YYYY-MM") from e

    total_saved = 0.0

    for tr in transactions:
        try:
            # Поддерживаем оба формата даты из DataFrame и списка словарей
            tr_date_str = tr["Дата операции"]
            if isinstance(tr_date_str, pd.Timestamp):
                tr_date = tr_date_str.to_pydatetime()
            elif isinstance(tr_date_str, datetime):
                tr_date = tr_date_str
            else:
                tr_date = datetime.strptime(tr_date_str, "%Y-%m-%d")
        except (ValueError, TypeError) as e:
            logger.warning(f"Неверный формат даты в транзакции: {tr.get('Дата операции')}. Пропущена.")
            continue

        if target_month_start <= tr_date < next_month_start:
            amount = abs(tr.get("Сумма операции", 0))
            if amount > 0:  # Только расходы
                rounded_amount = math.ceil(amount / limit) * limit
                saved = rounded_amount - amount
                total_saved += saved
                logger.debug(f"Транзакция {amount} -> округлена до {rounded_amount}, отложено {saved:.2f}")

    logger.info(f"За месяц {month} отложено в инвесткопилку: {total_saved:.2f} RUB")
    return round(total_saved, 2)


def investment_bank_from_df(target_date: str, df: pd.DataFrame, limit: int) -> float:
    """
    Рассчитывает сумму, отложенную в инвесткопилку за месяц,
    соответствующий указанной дате, используя DataFrame с транзакциями.
    """
    try:
        if len(target_date) > 10:
            target_datetime = datetime.strptime(target_date, "%Y-%m-%d %H:%M:%S")
        else:
            target_datetime = datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError as e:
        logger.error(f"Неверный формат целевой даты: {target_date}")
        raise ValueError("Дата должна быть в формате YYYY-MM-DD или YYYY-MM-DD HH:MM:SS") from e

    month_str = target_datetime.strftime("%Y-%m")
    transactions_list = df.to_dict("records")  # DataFrame уже в нужном формате
    return investment_bank(month_str, transactions_list, limit)
