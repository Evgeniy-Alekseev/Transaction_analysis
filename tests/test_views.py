import pytest
from unittest.mock import patch, MagicMock
from src.views import main_page



def test_main_page_success(sample_transactions_df):
    """
    Тест для функции main_page, проверяющий успешное выполнение.
    Мокируем внутренние функции для изоляции и предсказуемости.
    """
    # Входные данные для моков
    mock_settings = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    mock_currency_result = [{"currency": "USD", "rate": 75.0}]
    mock_stock_result = [{"stock": "AAPL", "price": 150.00}]
    expected_total_spent = 135.47 + 273.90 + 129.00 + 4.94  # = 543.31
    expected_cashback = int(expected_total_spent // 100)  # = 5

    # Используем вложенные патчи для мокирования зависимостей
    with patch('src.views.load_user_settings', return_value=mock_settings) as mock_load_settings, \
            patch('src.views.get_currency_rates', return_value=mock_currency_result) as mock_get_currency_rates, \
            patch('src.views.get_stock_prices', return_value=mock_stock_result) as mock_get_stock_prices:

        # Вызов тестируемой функции
        from src.views import main_page
        result = main_page("2021-10-25 14:00:00", sample_transactions_df)

        # --- Проверки вызовов моков ---
        mock_load_settings.assert_called_once()
        mock_get_currency_rates.assert_called_once_with(["USD"])
        mock_get_stock_prices.assert_called_once_with(["AAPL"])

        # --- Проверки результата ---
        assert "greeting" in result
        assert result["greeting"] == "Добрый день"

        assert "cards" in result
        assert len(result["cards"]) == 1
        card_data = result["cards"][0]
        assert card_data["last_digits"] == "7197"
        # Используем pytest.approx для чисел с плавающей точкой
        assert card_data["total_spent"] == pytest.approx(expected_total_spent)
        assert card_data["cashback"] == expected_cashback
        assert len(card_data["top_transactions"]) == 4

        assert "currency_rates" in result
        currency_rates = result["currency_rates"]
        assert len(currency_rates) == 1, f"Ожидался 1 курс валюты, получено: {currency_rates}"
        assert currency_rates[0] == mock_currency_result[0]

        assert "stock_prices" in result
        stock_prices = result["stock_prices"]
        assert len(stock_prices) == 1, f"Ожидалась 1 цена акции, получено: {stock_prices}"
        assert stock_prices[0] == mock_stock_result[0]


@pytest.mark.parametrize("hour, expected_greeting", [
    (6, "Доброе утро"),
    (12, "Добрый день"),
    (18, "Добрый вечер"),
    (23, "Доброй ночи"),
    (5, "Доброй ночи"),
])
def test_main_page_greetings(sample_transactions_df, hour, expected_greeting, mock_api_responses):
    # Мокируем API валют, API акций и API ключи
    with patch('requests.get') as mock_requests_get, \
            patch('os.getenv') as mock_os_getenv:

        def getenv_side_effect(key, default=None):
            if key == "CURRENCY_API_KEY":
                return "test_currency_api_key"
            elif key == "STOCKS_API_KEY":
                return "test_stocks_api_key"
            return default

        mock_os_getenv.side_effect = getenv_side_effect

        def requests_get_side_effect(url, *args, **kwargs):
            if "exchangerates_data" in url and "apilayer.com" in url:
                return mock_api_responses["currency"]
            elif "api-ninjas.com" in url and "/sp500" in url:
                return mock_api_responses["stock"]
            else:
                raise Exception(f"Unexpected requests.get call to URL: {url}")

        mock_requests_get.side_effect = requests_get_side_effect

        # Для теста приветствия можно использовать пустые настройки, так как они не влияют на результат
        mock_settings = {"user_currencies": [], "user_stocks": []}
        with patch('src.utils.load_user_settings', return_value=mock_settings):
            date_str = f"2021-10-25 {hour:02d}:00:00"
            result = main_page(date_str, sample_transactions_df)
            assert result["greeting"] == expected_greeting

def test_main_page_invalid_date_format(sample_transactions_df):
    with pytest.raises(ValueError, match="Дата должна быть в формате YYYY-MM-DD HH:MM:SS"):
        main_page("invalid-date", sample_transactions_df)
