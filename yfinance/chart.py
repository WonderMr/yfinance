from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ChartMeta(BaseModel):
    exchangeTimezoneName: Optional[str] = None


class ChartQuote(BaseModel):
    open: Optional[List[Optional[float]]] = None
    close: Optional[List[Optional[float]]] = None
    high: Optional[List[Optional[float]]] = None
    low: Optional[List[Optional[float]]] = None
    volume: Optional[List[Optional[int]]] = None


class ChartAdjClose(BaseModel):
    adjclose: Optional[List[Optional[float]]] = None


class ChartIndicators(BaseModel):
    quote: Optional[List[ChartQuote]] = None
    adjclose: Optional[List[ChartAdjClose]] = None


class ChartResult(BaseModel):
    meta: ChartMeta
    timestamp: Optional[List[int]] = None
    indicators: Optional[ChartIndicators] = None


class Chart(BaseModel):
    result: List[ChartResult]
    error: Optional[Dict[str, Any]] = None


class ChartResponse(BaseModel):
    chart: Chart
