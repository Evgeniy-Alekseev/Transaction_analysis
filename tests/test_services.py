import pytest
from datetime import datetime
from unittest.mock import patch
from src.services import investment_bank
from typing import List, Dict, Any


def test_investment_bank_valid(sample_transactions: List[Dict[str, Any]]):
    assert investment_bank("2021-12", sample_transactions, 50) == 75.11

def test_investment_bank_invalid_limit(sample_transactions: List[Dict[str, Any]]):
    with pytest.raises(ValueError):
        investment_bank("2021-12", sample_transactions, 20)

@pytest.mark.parametrize("month,limit,expected", [
    ("2021-12", 10, 5.11),
    ("2021-12", 50, 75.11),
    ("2021-12", 100, 75.11),
])
def test_investment_bank_parametrized(month: str, limit: int, expected: float,
                                     sample_transactions: List[Dict[str, Any]]):
    assert investment_bank(month, sample_transactions, limit) == expected

@patch("src.services.logging.error")
def test_investment_bank_logging(mock_logging: Any, sample_transactions: List[Dict[str, Any]]):
    invalid_transactions = sample_transactions + [{"Дата операции": "31.12.2021"}]
    investment_bank("2021-12", invalid_transactions, 10)
    mock_logging.assert_called()
