import pytest
from unittest.mock import patch
import sys
import io
import json
from datetime import datetime


def test_run_main_page_success(temp_data_file, capsys):
    from src.main import run_main_page
    with patch('src.utils.requests.get') as mock_get:
        mock_response = type('MockResponse', (), {
            'json': lambda: {"rates": {"USD": 75.0}},
            'raise_for_status': lambda: None
        })
        mock_get.return_value = mock_response
        
        mock_settings = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
        with patch('src.utils.load_user_settings', return_value=mock_settings):
            run_main_page("2021-10-25 14:00:00", temp_data_file)
    
    captured = capsys.readouterr()
    assert "--- Результат 'Главная' ---" in captured.out
    try:
        start = captured.out.find('{')
        end = captured.out.rfind('}') + 1
        if start != -1 and end > start:
            json_str = captured.out[start:end]
            result = json.loads(json_str)
            assert "greeting" in result
            assert "cards" in result
    except json.JSONDecodeError:
        assert "Добрый день" in captured.out
        assert "cards" in captured.out.lower()

def test_run_investment_bank_success(temp_data_file, capsys):
    from src.main import run_investment_bank
    run_investment_bank("2021-10-25", 50, temp_data_file)
    captured = capsys.readouterr()
    assert "--- Результат 'Инвесткопилка' ---" in captured.out
    # Проверим, что сумма отложена (на основе данных в temp_data_file)
    # 135.47 -> 150 (14.53)
    # 273.90 -> 300 (26.10)
    # Total = 40.63
    assert "40.63" in captured.out

def test_run_spending_report_success(temp_data_file, capsys):
    from src.main import run_spending_report
    from src.utils import load_transactions
    df = load_transactions(temp_data_file)
    run_spending_report("2021-10-25", temp_data_file)
    captured = capsys.readouterr()
    assert "--- Результат 'Траты по дням недели' ---" in captured.out
    assert ("Нет данных" in captured.out or "Monday" in captured.out)