import pandas as pd
import pytest
from datetime import datetime, timedelta
from src.reports import spending_by_weekday
import os
import json


def test_spending_by_weekday_success(sample_report_transactions_df, tmp_path):
    # Создаем уникальное имя файла для теста
    report_file = tmp_path / "test_weekday_report.json"

    # Применяем декоратор с параметром напрямую (имитация)
    from src.reports import report_to_file
    decorated_func = report_to_file(str(report_file))(spending_by_weekday)

    result_df = decorated_func(sample_report_transactions_df, "2023-09-24")  # Воскресенье

    assert result_df is not None
    assert not result_df.empty
    # Должно быть 7 дней
    assert len(result_df) == 7
    # Проверим, что столбцы правильные
    assert list(result_df.columns) == ['weekday', 'average_spent']
    # Проверим порядок дней
    expected_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    assert list(result_df['weekday']) == expected_days

    # Проверим, что файл был создан
    assert report_file.exists()

    # Проверим содержимое файла
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


# Тест для декоратора без параметра
def test_report_to_file_default_name(sample_report_transactions_df, tmp_path, monkeypatch):
    # Меняем рабочую директорию, чтобы файл создавался там
    monkeypatch.chdir(tmp_path)

    from src.reports import report_to_file
    decorated_func = report_to_file()(spending_by_weekday)  # Без имени файла

    result_df = decorated_func(sample_report_transactions_df, "2023-09-24")

    # Проверим, что файл был создан с дефолтным именем
    # Найдем файл, начинающийся с "report_spending_by_weekday_"
    import glob
    files = glob.glob("report_spending_by_weekday_*.json")
    assert len(files) == 1
    assert os.path.exists(files[0])

    # Проверим содержимое
    with open(files[0], 'r', encoding='utf-8') as f:
        file_data = json.load(f)
    assert len(file_data) == 7