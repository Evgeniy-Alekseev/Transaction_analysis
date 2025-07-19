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


# фикстуры для read_transactions_from_excel, get_greeting, report_decorator

@pytest.fixture
def sample_excel_data() -> bytes:
    """Фиктивные данные Excel файла"""
    df = pd.DataFrame({
        'Дата операции': ['31.12.2021 16:44:00', '30.12.2021 22:22:03'],
        'Сумма операции': [-160.89, -20000.0],
        'Категория': ['Супермаркеты', 'Переводы']
    })
    with pd.ExcelWriter('dummy.xlsx') as writer:
        df.to_excel(writer, index=False)
    with open('dummy.xlsx', 'rb') as f:
        return f.read()

@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    """Фиктивные транзакции"""
    return [
        {
            'Дата операции': '31.12.2021 16:44:00',
            'Сумма операции': -160.89,
            'Категория': 'Супермаркеты'
        },
        {
            'Дата операции': '30.12.2021 22:22:03',
            'Сумма операции': -20000.0,
            'Категория': 'Переводы'
        }
    ]
