from unittest.mock import Mock

import pytest

from yfinance.config import YfConfig
from yfinance.scrapers.history import PriceHistory


@pytest.mark.parametrize(
    ("bounds", "expected_start", "expected_end"),
    [
        ({"end": 0}, -2678400, 0),
        ({"end": "1970-01-01"}, -2678400, 0),
        ({"end": 0, "period": "5d"}, -432000, 0),
        ({"start": 0, "period": "5d"}, 0, 432000),
        ({"start": 0, "end": 86400}, 0, 86400),
        ({"start": -86400, "end": 0}, -86400, 0),
    ],
)
def test_epoch_history_bounds(monkeypatch, bounds, expected_start, expected_end):
    history = PriceHistory(Mock(), "TEST", tz="UTC", session=Mock())
    fetch = Mock(return_value=RuntimeError("stop after inspecting parameters"))
    monkeypatch.setattr(history, "_fetch_data", fetch)
    monkeypatch.setattr(YfConfig.debug, "hide_exceptions", True)

    history.history(**bounds)

    params = fetch.call_args.args[0]
    assert params["period1"] == expected_start
    assert params["period2"] == expected_end
    assert "range" not in params
