import pytest
from unittest.mock import patch, mock_open
from datetime import datetime
import pandas as pd
import json
from typing import List, Dict, Any
from src.utils import (
    read_transactions_from_excel,
    get_greeting,
    report_decorator
)



# Тесты для read_transactions_from_excel
def test_read_transactions_from_excel_success(sample_excel_data):
    """Тест успешного чтения Excel файла"""
    with patch('builtins.open', mock_open(read_data=sample_excel_data)), \
            patch('pandas.read_excel') as mock_read:
        mock_read.return_value = pd.DataFrame([{'test': 1}])
        result = read_transactions_from_excel('operations.xlsx')
        assert isinstance(result, list)
        mock_read.assert_called_once()


@patch('pandas.read_excel')
def test_read_transactions_from_excel_error(mock_read):
    """Тест обработки ошибки при чтении Excel"""
    mock_read.side_effect = Exception("Test error")
    with pytest.raises(Exception):
        read_transactions_from_excel('invalid.xlsx')


# Параметризованные тесты для get_greeting
@pytest.mark.parametrize("time_str, expected", [
    ("2023-01-01 08:00:00", "Доброе утро"),
    ("2023-01-01 13:00:00", "Добрый день"),
    ("2023-01-01 19:00:00", "Добрый вечер"),
    ("2023-01-01 03:00:00", "Доброй ночи"),
    ("invalid-time", "Добрый день"),  # Неверный формат времени
])
def test_get_greeting(time_str: str, expected: str):
    """Тест функции определения приветствия"""
    assert get_greeting(time_str) == expected


# Тесты для report_decorator
def test_report_decorator_without_filename(tmp_path, sample_transactions):
    """Тест декоратора без указания имени файла"""

    @report_decorator()
    def dummy_func():
        return sample_transactions

    result = dummy_func()
    assert result == sample_transactions
    # Проверяем, что файл был создан
    files = list(tmp_path.glob('report_*.json'))
    assert len(files) == 0


def test_report_decorator_with_filename(tmp_path, sample_transactions):
    """Тест декоратора с указанием имени файла"""
    test_file = tmp_path / "test_report.json"

    @report_decorator(str(test_file))
    def dummy_func():
        return sample_transactions

    result = dummy_func()
    assert result == sample_transactions
    assert test_file.exists()

    # Проверяем содержимое файла
    with open(test_file, 'r') as f:
        content = json.load(f)
    assert content == sample_transactions


def test_report_decorator_with_dataframe(tmp_path):
    """Тест декоратора с DataFrame"""
    df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    test_file = tmp_path / "df_report.json"

    @report_decorator(str(test_file))
    def dummy_func():
        return df

    result = dummy_func()
    assert test_file.exists()

    # Проверяем, что файл содержит DataFrame в JSON
    with open(test_file, 'r') as f:
        content = json.load(f)
    assert isinstance(content, list)
    assert len(content) == 2


@patch('builtins.open', side_effect=Exception("Test error"))
def test_report_decorator_error(mock_open):
    """Тест обработки ошибки при сохранении отчета"""

    @report_decorator()
    def dummy_func():
        return {'test': 'data'}

    result = dummy_func()
    assert result == {'test': 'data'}
    mock_open.assert_called()


# Тест логирования ошибок
@patch('src.utils.logging.error')
def test_get_greeting_logging_error(mock_logging):
    """Тест логирования ошибки в get_greeting"""
    get_greeting("invalid-time")
    mock_logging.assert_called_once_with("Invalid time format")


@patch('src.utils.logging.error')
def test_report_decorator_logging_error(mock_logging, tmp_path):
    """Тест логирования ошибки в report_decorator"""

    @report_decorator(str(tmp_path / "invalid" / "report.json"))
    def dummy_func():
        return {'test': 'data'}

    dummy_func()
    mock_logging.assert_called()
