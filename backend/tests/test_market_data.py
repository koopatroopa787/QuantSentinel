"""Unit tests for backend.tools.market_data."""

from __future__ import annotations

import sys
from pathlib import Path

# market_data.py (like the rest of backend/tools and backend/agents) imports its
# sibling modules as bare `tools.*`, which only resolves when `backend/` itself is
# on sys.path (the layout used when the app runs via `uvicorn main:app` from
# `backend/`). Add it here so this test can import the module the same way.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import market_data  # noqa: E402
from tools.cache import get as get_cached  # noqa: E402


def test_fetch_fomc_dates_without_api_key_uses_fallback(monkeypatch):
    """Regression test: fetch_fomc_dates must not crash when FRED_API_KEY is
    unset (the default on a fresh clone). It previously raised a NameError
    because `logger` was referenced but never defined in market_data.py.
    """
    monkeypatch.delenv("FRED_API_KEY", raising=False)

    result = market_data.fetch_fomc_dates(start_year=2023, end_year=2024)

    assert result["status"] == "success"
    assert result["source"] == "fallback"
    assert result["date_count"] > 0

    dates = get_cached(result["cache_key"])
    assert dates is not None
    assert all(2023 <= int(date[:4]) <= 2024 for date in dates)
