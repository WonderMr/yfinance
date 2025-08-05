import pandas as pd
import yfinance as yf
from yfinance.data import YfData
from yfinance.scrapers.history import PriceHistory

class MockResponse:
    def __init__(self, json_data):
        self._json = json_data
        self.text = ""
    def json(self):
        return self._json


def test_retry_empty_rows(monkeypatch):
    meta = {
        "instrumentType": "EQUITY",
        "exchangeTimezoneName": "UTC",
        "currency": "USD",
    }
    json_missing = {
        "chart": {
            "result": [
                {
                    "meta": meta,
                    "timestamp": [0, 86400],
                    "indicators": {
                        "quote": [
                            {
                                "open": [None, 1.0],
                                "high": [None, 1.0],
                                "low": [None, 1.0],
                                "close": [None, 1.0],
                                "volume": [0, 1],
                            }
                        ],
                        "adjclose": [{"adjclose": [None, 1.0]}],
                    },
                    "events": {},
                }
            ],
            "error": None,
        }
    }
    json_filled = {
        "chart": {
            "result": [
                {
                    "meta": meta,
                    "timestamp": [0],
                    "indicators": {
                        "quote": [
                            {
                                "open": [1.0],
                                "high": [1.0],
                                "low": [1.0],
                                "close": [1.0],
                                "volume": [1],
                            }
                        ],
                        "adjclose": [{"adjclose": [1.0]}],
                    },
                    "events": {},
                }
            ],
            "error": None,
        }
    }

    responses = [MockResponse(json_missing), MockResponse(json_filled)]
    call = {"n": 0}

    def fake_get(**kwargs):
        resp = responses[call["n"]]
        call["n"] = min(call["n"] + 1, len(responses) - 1)
        return resp

    data = YfData()
    monkeypatch.setattr(data, "get", fake_get)
    monkeypatch.setattr(data, "cache_get", fake_get)

    ph = PriceHistory(data, "TEST", tz="UTC")
    df = ph.history(start="1970-01-01", end="1970-01-03", interval="1d", actions=False, auto_adjust=False, keepna=True)

    assert not df.iloc[0].isna().all()
    assert len(df) == 2
