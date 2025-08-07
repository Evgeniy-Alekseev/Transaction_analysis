from src.services import investment_bank, investment_bank_from_df
import pytest
import math
import pandas as pd
from datetime import datetime

def test_investment_bank_success(sample_investment_bank_transactions):
    # limit=50
    # 1712.0 -> 1750.0 (38.0)
    # 50.0 -> 50.0 (0.0)
    # 99.99 -> 100.0 (0.01)
    # Итого: 38.01
    result = investment_bank("2023-10", sample_investment_bank_transactions, 50)
    assert result == 38.01

@pytest.mark.parametrize("limit, expected_saved", [
    (10, 8.01),   # 1712->1720(8), 50->50(0), 100->100(0), 99.99->100(0.01)
    (50, 38.01),  # 1712->1750(38), 50->50(0), 100->100(0), 99.99->100(0.01)
    (100, 138.01), # 1712->1800(88), 50->100(50), 100->100(0), 99.99->100(0.01)
])
def test_investment_bank_limits(sample_investment_bank_transactions, limit, expected_saved):
    result = investment_bank("2023-10", sample_investment_bank_transactions, limit)
    # Из-за округления вручную пересчитаем ожидаемое значение
    if limit == 100:
        expected_saved = 138.01
    assert result == expected_saved

def test_investment_bank_invalid_month():
    with pytest.raises(ValueError, match="Месяц должен быть в формате YYYY-MM"):
        investment_bank("invalid-month", [], 50)

def test_investment_bank_invalid_limit(sample_investment_bank_transactions):
    # limit=999 -> default to 50
    # 1712.0: ceil(1712.0/50)*50 = 35*50=1750. Saved=38.0
    # 50.0: ceil(50.0/50)*50 = 1*50=50. Saved=0.0
    # 100.0: ceil(100.0/50)*50 = 2*50=100. Saved=0.0 (не входит в октябрь)
    # 99.99: ceil(99.99/50)*50 = 2*50=100. Saved=0.01
    # Total = 38.0 + 0.0 + 0.01 = 38.01
    result = investment_bank("2023-10", sample_investment_bank_transactions, 999)
    assert result == 38.01

def test_investment_bank_no_transactions():
    result = investment_bank("2023-10", [], 50)
    assert result == 0.0

def test_investment_bank_wrong_month_transactions(sample_investment_bank_transactions):
    # Транзакции только за 2023-10, запрос за 2023-09
    result = investment_bank("2023-09", sample_investment_bank_transactions, 50)
    assert result == 0.0

# Тест с некорректной датой в транзакции
def test_investment_bank_invalid_transaction_date():
    transactions = [
        {"Дата операции": "2023-10-15", "Сумма операции": -100.0},
        {"Дата операции": "invalid-date", "Сумма операции": -50.0}, # Некорректная дата
        {"Дата операции": "2023-10-20", "Сумма операции": -200.0},
    ]
    result = investment_bank("2023-10", transactions, 50)
    # Должны обработать только 15 и 20 октября
    # 100.0 -> 100.0 (0.0)
    # 200.0 -> 200.0 (0.0)
    # Total = 0.0
    assert result == 0.0

# Тест с положительной суммой (доход)
def test_investment_bank_income_ignored():
    transactions = [
        {"Дата операции": "2023-10-15", "Сумма операции": -100.0},
        {"Дата операции": "2023-10-16", "Сумма операции": 500.0}, # Доход
        {"Дата операции": "2023-10-20", "Сумма операции": -200.0},
    ]
    result = investment_bank("2023-10", transactions, 50)
    # Только расходы: 100.0 -> 100.0 (0.0), 200.0 -> 200.0 (0.0)
    assert result == 0.0


def test_investment_bank_from_df_success(sample_transactions_df):
    # Используем DataFrame с данными за октябрь 2021
    # 135.47, 273.90, 129.00, 4.94
    # limit=50
    # 135.47 -> 150 (14.53)
    # 273.90 -> 300 (26.10)
    # 129.00 -> 150 (21.00)
    # 4.94 -> 50 (45.06)
    # Total = 14.53 + 26.10 + 21.00 + 45.06 = 106.69
    result = investment_bank_from_df("2021-10-25", sample_transactions_df, 50)
    assert result == 106.69

def test_investment_bank_from_df_datetime_format(sample_transactions_df):
    result = investment_bank_from_df("2021-10-25 14:00:00", sample_transactions_df, 50)
    assert result == 106.69

def test_investment_bank_from_df_invalid_date(sample_transactions_df):
    with pytest.raises(ValueError, match="Дата должна быть в формате"):
        investment_bank_from_df("invalid-date", sample_transactions_df, 50)

# Тест с данными из файла operations.xlsx (имитация)
def test_investment_bank_from_df_realistic_data():
    # Создаем DataFrame, имитирующий часть данных из operations.xlsx
    data = {
        'Дата операции': pd.to_datetime(['31.12.2021 16:44:00', '31.12.2021 16:42:04', '31.12.2021 16:39:04'], format='%d.%m.%Y %H:%M:%S'),
        'Сумма операции': [-160.89, -64.00, -118.12]
    }
    df = pd.DataFrame(data)
    
    # limit=50
    # 160.89 -> 200 (39.11)
    # 64.00 -> 100 (36.00)
    # 118.12 -> 150 (31.88)
    # Total = 39.11 + 36.00 + 31.88 = 106.99
    result = investment_bank_from_df("2021-12-31", df, 50)
    assert result == 106.99