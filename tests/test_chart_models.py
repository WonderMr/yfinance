from tests.context import yfinance as yf

import unittest
from unittest.mock import Mock

from pydantic import ValidationError

from yfinance.chart import ChartResponse


SAMPLE_CHART_RESPONSE = {
    "chart": {
        "result": [
            {
                "meta": {"exchangeTimezoneName": "America/New_York"},
                "timestamp": [0],
                "indicators": {
                    "quote": [
                        {
                            "open": [1.0],
                            "close": [1.0],
                            "high": [1.0],
                            "low": [1.0],
                            "volume": [100],
                        }
                    ]
                },
            }
        ],
        "error": None,
    }
}


class TestChartModels(unittest.TestCase):
    def test_model_parses_timezone(self):
        chart = ChartResponse.model_validate(SAMPLE_CHART_RESPONSE)
        self.assertEqual(
            chart.chart.result[0].meta.exchangeTimezoneName,
            "America/New_York",
        )

    def test_fetch_ticker_tz_uses_model(self):
        ticker = yf.Ticker("FAKE")
        mock_resp = Mock()
        mock_resp.json.return_value = SAMPLE_CHART_RESPONSE
        original_cache_get = ticker._data.cache_get
        ticker._data.cache_get = Mock(return_value=mock_resp)
        try:
            tz = ticker._fetch_ticker_tz(timeout=5)
            self.assertEqual(tz, "America/New_York")
        finally:
            ticker._data.cache_get = original_cache_get

    def test_model_validation_error(self):
        bad_data = {"chart": {"result": [{}], "error": None}}
        with self.assertRaises(ValidationError):
            ChartResponse.model_validate(bad_data)
