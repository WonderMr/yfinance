from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd
import pytest

import yfinance as yf
from yfinance import cache
from yfinance.config import YfConfig
from yfinance.data import YfData
from yfinance.exceptions import YFDataException, YFRateLimitError
from yfinance.multi import YfConfig as MultiConfig
from yfinance.scrapers.history import PriceHistory
from yfinance.scrapers.history import YFRateLimitError as HistoryRateLimitError
from yfinance.scrapers.quote import FastInfo
from yfinance.screener.screener import screen
from yfinance.utils import _parse_user_dt, generate_list_table_from_dict_universal


def test_public_compatibility_exports():
    assert yf.YfData is YfData
    assert HistoryRateLimitError is YFRateLimitError
    assert MultiConfig is YfConfig
    assert yf.Ticker("TEST").ticker == "TEST"
    assert yf.Tickers("TEST").tickers["TEST"].ticker == "TEST"


def test_singleton_cache_interface(monkeypatch):
    data = YfData()
    response = object()
    get = Mock(return_value=response)
    monkeypatch.setattr(data, "get", get)
    data.cache_get.cache_clear()
    try:
        assert data.cache_get("https://example.invalid", params={"a": 1}) is response
        assert data.cache_get("https://example.invalid", params={"a": 1}) is response
        assert get.call_count == 1
        assert data.cache_get.cache_info().hits == 1
    finally:
        data.cache_get.cache_clear()


def test_session_cache_property_is_evaluated():
    accesses = []

    class CachedSession:
        @property
        def cache(self):
            accesses.append(True)
            return {}

    with pytest.raises(YFDataException, match="request_cache"):
        YfData()._set_session(CachedSession())
    assert accesses == [True]


def test_fast_info_fallback_evaluates_info(monkeypatch):
    class LazyTicker:
        def __init__(self):
            self._quote = SimpleNamespace(_retired_info=None)
            self.accesses = 0

        @property
        def info(self):
            self.accesses += 1
            self._quote._retired_info = {"previousClose": 12.5}
            return {}

    ticker = LazyTicker()
    info = FastInfo(ticker)
    monkeypatch.setattr(info, "_get_1wk_1h_prepost_prices", lambda: pd.DataFrame())
    assert info.previous_close == 12.5
    assert ticker.accesses == 1


@pytest.mark.parametrize("manager", [cache._TzDBManager, cache._CookieDBManager, cache._ISINDBManager])
def test_database_close_preserves_shutdown_suppression(monkeypatch, manager):
    database = Mock()
    database.close.side_effect = RuntimeError("database finalizing")
    monkeypatch.setattr(manager, "_db", database)
    manager.close_db()
    database.close.assert_called_once()


def test_validation_keeps_value_error_api():
    with pytest.raises(ValueError):
        _parse_user_dt(1.5, "UTC")
    with pytest.raises(ValueError):
        screen(object())
    history = PriceHistory(Mock(), "TEST", "UTC", session=Mock())
    with pytest.raises(ValueError):
        history._reconstruct_intervals_batch([], "1d", False)


def test_table_default_matches_explicit_empty_keys():
    data = {"category": {"field": {"value"}}}
    assert generate_list_table_from_dict_universal(data) == generate_list_table_from_dict_universal(data, concat_keys=[])
