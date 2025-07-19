import pandas as pd
import json
from datetime import datetime
import logging
from typing import List, Dict, Any, Optional
import functools
import os

def read_transactions_from_excel(filepath: str) -> List[Dict[str, Any]]:
    """Чтение транзакций из Excel-файла"""
    try:
        df = pd.read_excel(filepath)
        return df.to_dict('records')
    except Exception as e:
        logging.error(f"Error reading Excel file: {e}")
        raise

def get_greeting(time_str: str) -> str:
    """Возвращает приветствие в зависимости от времени"""
    try:
        time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").time()
        if 5 <= time.hour < 12:
            return "Доброе утро"
        elif 12 <= time.hour < 17:
            return "Добрый день"
        elif 17 <= time.hour < 23:
            return "Добрый вечер"
        else:
            return "Доброй ночи"
    except ValueError:
        logging.error("Invalid time format")
        return "Добрый день"

def report_decorator(filename: Optional[str] = None):
    """Декоратор для сохранения отчетов в файл"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            output_file = filename or f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(output_file, 'w') as f:
                    if isinstance(result, pd.DataFrame):
                        result.to_json(f, orient='records', force_ascii=False)
                    else:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                logging.info(f"Report saved to {output_file}")
            except Exception as e:
                logging.error(f"Error saving report: {e}")
            return result
        return wrapper
    return decorator
