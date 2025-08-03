import math
from datetime import datetime
from typing import List, Dict, Any
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """
    Рассчитывает сумму, отложенную в инвесткопилку за указанный месяц.
    (Оригинальная функция из задания, работает со списком словарей)
    """
    logger.info(f"Расчет инвесткопилки для месяца {month} с лимитом {limit}")

    if limit not in [10, 50, 100]:
        logger.warning(f"Некорректный лимит округления: {limit}. Используется 10.")
        limit = 10

    try:
        target_month_start = datetime.strptime(month, '%Y-%m')
        # next_month_start = target_month_start.replace(month=target_month_start.month + 1) if target_month_start.month < 12 else target_month_start.replace(year=target_month_start.year + 1, month=1)
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
            tr_date = datetime.strptime(tr['Дата операции'], '%Y-%m-%d')
        except ValueError:
            logger.warning(f"Неверный формат даты в транзакции: {tr.get('Дата операции')}")
            continue

        if target_month_start <= tr_date < next_month_start:
            amount = abs(tr.get('Сумма операции', 0))
            if amount > 0:  # Только расходы
                rounded_amount = math.ceil(amount / limit) * limit
                saved = rounded_amount - amount
                total_saved += saved
                logger.debug(f"Транзакция {amount} -> округлена до {rounded_amount}, отложено {saved}")

    logger.info(f"За месяц {month} отложено в инвесткопилку: {total_saved:.2f} RUB")
    return round(total_saved, 2)


def investment_bank_from_df(target_date: str, df: pd.DataFrame, limit: int) -> float:
    """
    Рассчитывает сумму, отложенную в инвесткопилку за месяц,
    соответствующий указанной дате, используя DataFrame с транзакциями.

    Args:
        target_date: Дата в формате 'YYYY-MM-DD' или 'YYYY-MM-DD HH:MM:SS'.
                     Месяц этой даты будет использован для расчета.
        df: DataFrame с транзакциями.
        limit: Предел округления (10, 50, 100).

    Returns:
        Сумма, отложенная в инвесткопилку.
    """
    try:
        # Поддерживаем оба формата даты
        if len(target_date) > 10:  # 'YYYY-MM-DD HH:MM:SS'
            target_datetime = datetime.strptime(target_date, '%Y-%m-%d %H:%M:%S')
        else:  # 'YYYY-MM-DD'
            target_datetime = datetime.strptime(target_date, '%Y-%m-%d')
    except ValueError as e:
        logger.error(f"Неверный формат целевой даты: {target_date}")
        raise ValueError("Дата должна быть в формате YYYY-MM-DD или YYYY-MM-DD HH:MM:SS") from e

    month_str = target_datetime.strftime('%Y-%m')

    # Конвертируем DataFrame в список словарей для совместимости
    # Убеждаемся, что дата в нужном формате для investment_bank
    transactions_list = []
    for _, row in df.iterrows():
        tr_dict = row.to_dict()
        # Формат даты в файле: datetime64[ns], формат для функции: 'YYYY-MM-DD'
        if pd.notna(tr_dict.get('Дата операции')):
            tr_dict['Дата операции'] = tr_dict['Дата операции'].strftime('%Y-%m-%d')
        transactions_list.append(tr_dict)

    return investment_bank(month_str, transactions_list, limit)
