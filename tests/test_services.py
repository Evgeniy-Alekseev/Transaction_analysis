from src.services import investment_bank
import pytest
import math

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
    (100, 88.01), # 1712->1800(88), 50->100(50), 100->100(0), 99.99->100(0.01) -> 88+50+0+0.01=138.01 ?
    # Давайте пересчитаем для 100:
    # 1712.0: ceil(1712.0/100)*100 = 18*100=1800. Saved=88.0
    # 50.0: ceil(50.0/100)*100 = 1*100=100. Saved=50.0
    # 100.0: ceil(100.0/100)*100 = 1*100=100. Saved=0.0
    # 99.99: ceil(99.99/100)*100 = 1*100=100. Saved=0.01
    # Total = 88.0 + 50.0 + 0.0 + 0.01 = 138.01
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
    # limit=999 -> default to 10
    # 1712.0: ceil(1712.0/10)*10 = 172*10=1720. Saved=8.0
    # 50.0: ceil(50.0/10)*10 = 5*10=50. Saved=0.0
    # 100.0: ceil(100.0/10)*10 = 10*10=100. Saved=0.0
    # 99.99: ceil(99.99/10)*10 = 10*10=100. Saved=0.01
    # Total = 8.0 + 0.0 + 0.0 + 0.01 = 8.01
    result = investment_bank("2023-10", sample_investment_bank_transactions, 999)
    assert result == 8.01

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