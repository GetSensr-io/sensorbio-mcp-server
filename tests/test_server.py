"""Unit tests for server tools and utilities.

All tests run offline — no API credentials required.
"""

from __future__ import annotations

import re
from datetime import date

import pytest

from sensorbio_mcp_server.utils import (
    cursor_from_next_link,
    expand_date_range,
    make_range_summary,
    strip_sleep_payload,
    today_str,
)

# ---------------------------------------------------------------------------
# today_str
# ---------------------------------------------------------------------------


def test_today_str_format():
    result = today_str()
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", result)
    # Should be parseable
    date.fromisoformat(result)


def test_today_str_with_tz():
    result = today_str(tz="UTC")
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", result)


# ---------------------------------------------------------------------------
# expand_date_range
# ---------------------------------------------------------------------------


def test_expand_date_range_default_is_today():
    dr = expand_date_range()
    assert len(dr.dates) == 1
    assert dr.dates[0] == today_str()


def test_expand_date_range_single_date():
    dr = expand_date_range(date_str="2026-01-15")
    assert dr.dates == ["2026-01-15"]


def test_expand_date_range_start_end():
    dr = expand_date_range(start_date="2026-03-01", end_date="2026-03-03")
    assert dr.dates == ["2026-03-01", "2026-03-02", "2026-03-03"]


def test_expand_date_range_days():
    dr = expand_date_range(days=1)
    assert len(dr.dates) == 1
    assert dr.dates[0] == today_str()


def test_expand_date_range_days_3():
    dr = expand_date_range(days=3)
    assert len(dr.dates) == 3


def test_expand_date_range_end_before_start_raises():
    with pytest.raises(ValueError, match="end_date must be >= start_date"):
        expand_date_range(start_date="2026-03-05", end_date="2026-03-01")


def test_expand_date_range_days_zero_raises():
    with pytest.raises(ValueError, match="days must be >= 1"):
        expand_date_range(days=0)


def test_expand_date_range_missing_end_date_raises():
    with pytest.raises(ValueError):
        expand_date_range(start_date="2026-03-01")


# ---------------------------------------------------------------------------
# strip_sleep_payload
# ---------------------------------------------------------------------------


def test_strip_sleep_payload_removes_time_series():
    payload = {
        "data": {
            "sleep_score": 85,
            "time_series": [1, 2, 3],
            "timeseries": [4, 5, 6],
            "epochs": [7, 8, 9],
        }
    }
    result = strip_sleep_payload(payload)
    assert "time_series" not in result["data"]
    assert "timeseries" not in result["data"]
    assert "epochs" not in result["data"]
    assert result["data"]["sleep_score"] == 85


def test_strip_sleep_payload_nested_sleep():
    payload = {
        "data": {
            "sleep": {
                "duration": 28800,
                "time_series": [1, 2, 3],
                "raw": [4, 5],
            }
        }
    }
    result = strip_sleep_payload(payload)
    assert "time_series" not in result["data"]["sleep"]
    assert "raw" not in result["data"]["sleep"]
    assert result["data"]["sleep"]["duration"] == 28800


def test_strip_sleep_payload_no_data():
    assert strip_sleep_payload({}) == {}
    assert strip_sleep_payload({"data": None}) == {"data": None}


def test_strip_sleep_payload_not_dict():
    assert strip_sleep_payload("not a dict") == "not a dict"


# ---------------------------------------------------------------------------
# make_range_summary
# ---------------------------------------------------------------------------


def test_make_range_summary_basic():
    results = [
        {"date": "2026-03-01", "data": {}},
        {"date": "2026-03-02", "data": {}},
        {"date": "2026-03-03", "data": {}},
    ]
    summary = make_range_summary(results)
    assert summary["days"] == 3
    assert summary["start_date"] == "2026-03-01"
    assert summary["end_date"] == "2026-03-03"


def test_make_range_summary_empty():
    summary = make_range_summary([])
    assert summary["days"] == 0
    assert summary["start_date"] is None
    assert summary["end_date"] is None


def test_make_range_summary_single():
    summary = make_range_summary([{"date": "2026-03-14", "data": {}}])
    assert summary["days"] == 1
    assert summary["start_date"] == "2026-03-14"
    assert summary["end_date"] == "2026-03-14"


# ---------------------------------------------------------------------------
# cursor_from_next_link
# ---------------------------------------------------------------------------


def test_cursor_from_next_link_none():
    assert cursor_from_next_link(None) is None


def test_cursor_from_next_link_no_cursor():
    assert cursor_from_next_link("https://api.sensorbio.com/v1/activities?limit=50") is None


def test_cursor_from_next_link_with_cursor():
    assert cursor_from_next_link("https://api.sensorbio.com/v1/x?cursor=abc123") == "abc123"


# ---------------------------------------------------------------------------
# Tool functions exist and return error dicts without auth
# ---------------------------------------------------------------------------


def test_tool_functions_importable():
    """All declared tool functions should be importable."""
    from sensorbio_mcp_server.server import (
        debug_request,
        get_activities,
        get_biometrics,
        get_calories,
        get_org_scores_summary,
        get_org_sleep_summary,
        get_scores,
        get_sleep,
        get_user_by_email,
        get_user_ids,
        list_users,
        search_user,
    )

    # All should be callable
    assert callable(list_users)
    assert callable(get_user_ids)
    assert callable(get_user_by_email)
    assert callable(search_user)
    assert callable(get_sleep)
    assert callable(get_scores)
    assert callable(get_activities)
    assert callable(get_biometrics)
    assert callable(get_calories)
    assert callable(get_org_sleep_summary)
    assert callable(get_org_scores_summary)
    assert callable(debug_request)


def test_tools_return_error_without_auth(monkeypatch: pytest.MonkeyPatch):
    """Without auth env vars, tool functions should return error dicts, not raise."""
    for k in ["SENSR_ORG_TOKEN", "SENSR_API_KEY", "SENSR_CLIENT_ID", "SENSR_CLIENT_SECRET"]:
        monkeypatch.delenv(k, raising=False)

    from sensorbio_mcp_server.server import get_scores, get_sleep, list_users

    r = list_users()
    assert "error" in r
    assert "message" in r["error"]

    r = get_sleep("fake_user_id", date="2026-03-14")
    assert "error" in r

    r = get_scores("fake_user_id", date="2026-03-14")
    assert "error" in r
