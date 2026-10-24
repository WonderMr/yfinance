from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ChartMeta(BaseModel):
    exchangeTimezoneName: str | None = None


class ChartQuote(BaseModel):
    open: list[float | None] | None = None
    close: list[float | None] | None = None
    high: list[float | None] | None = None
    low: list[float | None] | None = None
    volume: list[int | None] | None = None


class ChartAdjClose(BaseModel):
    adjclose: list[float | None] | None = None


class ChartIndicators(BaseModel):
    quote: list[ChartQuote] | None = None
    adjclose: list[ChartAdjClose] | None = None


class ChartResult(BaseModel):
    meta: ChartMeta
    timestamp: list[int] | None = None
    indicators: ChartIndicators | None = None


class Chart(BaseModel):
    result: list[ChartResult]
    error: dict[str, Any] | None = None


class ChartResponse(BaseModel):
    chart: Chart
