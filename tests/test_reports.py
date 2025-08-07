import pandas as pd
import pytest
from datetime import datetime, timedelta
from src.reports import spending_by_weekday
import os
import json


def test_spending_by_weekday_success(sample_report_transactions_df, tmp_path):
    report_file = tmp_path / "test_weekday_report.json"
    
    from src.reports import report_to_file
    decorated_func = report_to_file(str(report_file))(spending_by_weekday)
    
    result_df = decorated_func(sample_report_transactions_df, "2023-09-24")
    
    assert result_df is not None
    assert not result_df.empty
    assert len(result_df) == 7
    assert list(result_df.columns) == ['weekday', 'average_spent']
    expected_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    assert list(result_df['weekday']) == expected_days
    
    assert report_file.exists()
    
    with open(report_file, 'r', encoding='utf-8') as f:
        file_data = json.load(f)
    assert isinstance(file_data, list)
    assert len(file_data) == 7
    assert file_data[0]['weekday'] == 'Monday'


def test_spending_by_weekday_no_data():
    empty_df = pd.DataFrame(columns=['Дата операции', 'Сумма операции'])
    result_df = spending_by_weekday(empty_df, "2023-09-24")
    assert result_df is not None
    assert result_df.empty


def test_spending_by_weekday_invalid_date(sample_report_transactions_df):
    with pytest.raises(ValueError, match="Дата должна быть в формате YYYY-MM-DD"):
        spending_by_weekday(sample_report_transactions_df, "invalid-date")


def test_spending_by_weekday_default_date(sample_report_transactions_df, monkeypatch):
    # Замокаем datetime.now для предсказуемости
    fixed_date = datetime(2023, 9, 24)  # Воскресенье

    class MockDateTime:
        @classmethod
        def now(cls):
            return fixed_date

    monkeypatch.setattr('src.reports.datetime', MockDateTime)

    result_df = spending_by_weekday(sample_report_transactions_df)  # Без даты
    assert result_df is not None
    assert not result_df.empty
    assert len(result_df) == 7


def test_report_to_file_default_name(sample_report_transactions_df, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    from src.reports import report_to_file
    decorated_func = report_to_file()(spending_by_weekday)
    
    result_df = decorated_func(sample_report_transactions_df, "2023-09-24")
    
    import glob
    files = glob.glob("report_spending_by_weekday_*.json")
    assert len(files) == 1
    assert os.path.exists(files[0])
    
    with open(files[0], 'r', encoding='utf-8') as f:
        file_data = json.load(f)
    assert len(file_data) == 7

def test_report_to_file_empty_result(tmp_path):
    empty_df = pd.DataFrame(columns=['Дата операции', 'Сумма операции'])
    empty_df['Дата операции'] = pd.to_datetime(empty_df['Дата операции'])
    
    report_file = tmp_path / "empty_report.json"
    from src.reports import report_to_file
    decorated_func = report_to_file(str(report_file))(spending_by_weekday)
    
    result_df = decorated_func(empty_df, "2023-09-24")
    
    # Файл не должен быть создан для пустого результата
    assert not report_file.exists()
    assert result_df.empty