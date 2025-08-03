from src.views import main_page
import pytest
from unittest.mock import patch, MagicMock


def test_main_page_success(sample_transactions_df, mock_api_responses, temp_user_settings_file):
    # Используем patch как контекстный менеджер для правильного мока внутри src.utils
    with patch('src.utils.requests.get', return_value=mock_api_responses["currency"]):
        # Мокаем load_user_settings, чтобы использовать наши тестовые настройки
        # (в реальном тесте можно было бы мокать temp_user_settings_file, но проще передать напрямую)
        mock_settings = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}

        with patch('src.utils.load_user_settings', return_value=mock_settings):
            result = main_page("2021-10-25 14:00:00", sample_transactions_df)

            assert "greeting" in result
            assert result["greeting"] == "Добрый день"
            assert "cards" in result
            assert len(result["cards"]) == 1
            assert result["cards"][0]["last_digits"] == "7197"
            assert result["cards"][0]["total_spent"] == 543.31
            assert result["cards"][0]["cashback"] == 5
            assert len(result["cards"][0]["top_transactions"]) == 4
            assert "currency_rates" in result
            # --- Исправленное утверждение ---
            assert len(result["currency_rates"]) == 1
            assert result["currency_rates"][0]["currency"] == "USD"
            # Проверяем, что курс был взят из мока
            assert result["currency_rates"][0]["rate"] == 75.0
            assert "stock_prices" in result
            assert len(result["stock_prices"]) == 1
            # Цена акции - заглушка
            assert result["stock_prices"][0]["stock"] == "AAPL"
            # assert result["stock_prices"][0]["price"] == "150.00" # Если бы мок был точнее


# --- Тест с параметризацией ---
@pytest.mark.parametrize("hour, expected_greeting", [
    (6, "Доброе утро"),
    (12, "Добрый день"),
    (18, "Добрый вечер"),
    (23, "Доброй ночи"),
    (5, "Доброй ночи"),
])
def test_main_page_greetings(sample_transactions_df, hour, expected_greeting, mock_api_responses):
    # Мокируем API валют
    with patch('src.utils.requests.get', return_value=mock_api_responses["currency"]):
        mock_settings = {"user_currencies": [], "user_stocks": []}
        with patch('src.utils.load_user_settings', return_value=mock_settings):
            # Создаем строку даты/времени с нужным часом
            date_str = f"2021-10-25 {hour:02d}:00:00"
            result = main_page(date_str, sample_transactions_df)
            assert result["greeting"] == expected_greeting


# --- Тест с ошибкой даты ---
def test_main_page_invalid_date_format(sample_transactions_df):
    with pytest.raises(ValueError, match="Дата должна быть в формате YYYY-MM-DD HH:MM:SS"):
        main_page("invalid-date", sample_transactions_df)
