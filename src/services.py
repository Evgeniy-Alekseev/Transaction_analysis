from typing import List, Dict, Any
from datetime import datetime
import logging
import functools


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """
    Рассчитывает сумму для инвесткопилки через округление трат

    Args:
        month: Месяц в формате 'YYYY-MM'
        transactions: Список транзакций
        limit: Предел округления (10, 50 или 100)

    Returns:
        Сумма для инвесткопилки
    """
    if limit not in {10, 50, 100}:
        raise ValueError("Предел округления должен быть 10, 50 или 100 ₽.")

    total_saved = 0.0
    year, month_num = map(int, month.split('-'))

    for transaction in transactions:
        try:
            date_str = transaction.get("Дата операции")
            if not date_str:
                continue

            date = datetime.strptime(date_str.split()[0], "%d.%m.%Y")
            if date.year != year or date.month != month_num:
                continue

            amount = transaction.get("Сумма операции")
            if amount is None or amount >= 0:
                continue

            rounded_amount = ((abs(amount) + limit - 1) // limit) * limit
            saved = rounded_amount - abs(amount)
            total_saved += saved

        except Exception as e:
            logging.error(f"Ошибка обработки транзакции: {transaction}. Ошибка: {e}")

    return round(total_saved, 2)
