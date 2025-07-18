import pytest
from typing import List, Dict, Any


# фикстуры для investment_bank

@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    return [
        {"Дата операции": "31.12.2021 16:44:00", "Сумма операции": -160.89},
        {"Дата операции": "31.12.2021 16:42:04", "Сумма операции": -64.0},
        {"Дата операции": "30.11.2021 10:41:46", "Сумма операции": -103.0},  # Не должен учитываться
    ]
