import math
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """
    Рассчитывает сумму, отложенную в инвесткопилку за указанный месяц.

    Args:
        month: Месяц в формате 'YYYY-MM'.
        transactions: Список транзакций.
        limit: Предел округления (10, 50, 100).

    Returns:
        Сумма, отложенная в инвесткопилку.
    """
    logger.info(f"Расчет инвесткопилки для месяца {month} с лимитом {limit}")

    if limit not in [10, 50, 100]:
        logger.warning(f"Некорректный лимит округления: {limit}. Используется 10.")
        limit = 10

    try:
        target_month_start = datetime.strptime(month, '%Y-%m')
        next_month_start = target_month_start.replace(
            month=target_month_start.month + 1) if target_month_start.month < 12 else target_month_start.replace(
            year=target_month_start.year + 1, month=1)
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
                # Округление вверх до ближайшего лимита
                rounded_amount = math.ceil(amount / limit) * limit
                saved = rounded_amount - amount
                total_saved += saved
                logger.debug(f"Транзакция {amount} -> округлена до {rounded_amount}, отложено {saved}")

    logger.info(f"За месяц {month} отложено в инвесткопилку: {total_saved:.2f} RUB")
    return round(total_saved, 2)
