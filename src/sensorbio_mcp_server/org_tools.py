from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

from .sensr_client import SensrClient, error_dict
from .utils import expand_date_range, make_range_summary, strip_sleep_payload


def _get_org_user_ids(client: SensrClient, max_users: int) -> list[str] | dict[str, Any]:
    try:
        resp = client.request("GET", "/v1/organizations/users/ids")
        data = resp.get("user_ids")
        if not isinstance(data, list):
            return error_dict(
                message="Unexpected response shape for user ids",
                endpoint="/v1/organizations/users/ids",
                method="GET",
                status=200,
                body_preview=str(resp)[:1500],
            )
        return [str(x) for x in data][:max_users]
    except Exception as e:
        return error_dict(
            message=f"{type(e).__name__}: {e}",
            endpoint="/v1/organizations/users/ids",
            method="GET",
        )


def _fan_out(
    ids: list[str],
    fetch_one: Callable[[str], tuple[dict[str, Any], list[dict[str, Any]]]],
    concurrency: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Run fetch_one across ids concurrently, collecting records and errors.

    Threads rather than an event loop, for two reasons:

    * ``SensrClient.request`` is synchronous (``httpx.Client``), so the blocking
      HTTP calls are what needs parallelising. Wrapping them in an anyio task
      group added scheduling machinery without making anything concurrent.
    * ``anyio.run()`` raises ``RuntimeError: Already running asyncio in this
      thread`` whenever these helpers are called from an MCP server, because
      FastMCP is already running an event loop in the calling thread.

    ``fetch_one`` returns its own ``(record, errors)`` rather than appending to
    shared lists, so no locking is required.
    """
    records: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    if not ids:
        return records, errors
    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
        for record, record_errors in pool.map(fetch_one, ids):
            records.append(record)
            errors.extend(record_errors)
    return records, errors


def org_sleep_summary(
    *,
    client: SensrClient,
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    days: int | None = None,
    max_users: int = 50,
    concurrency: int = 5,
) -> dict[str, Any]:
    ids = _get_org_user_ids(client, max_users)
    if isinstance(ids, dict) and ids.get("error"):
        return ids

    dr = expand_date_range(date_str=date, start_date=start_date, end_date=end_date, days=days)

    def fetch_user(uid: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        user_days: list[dict[str, Any]] = []
        user_errors: list[dict[str, Any]] = []
        for d in dr.dates:
            try:
                resp = client.request("GET", "/v1/sleep", params={"user_id": uid, "date": d})
                resp = strip_sleep_payload(resp)
                user_days.append({"date": d, "data": resp.get("data")})
            except Exception as e:
                user_errors.append(
                    error_dict(
                        message=f"{type(e).__name__}: {e}",
                        endpoint="/v1/sleep",
                        method="GET",
                    )
                )
        record = {
            "user_id": uid,
            "days": user_days,
            "summary": make_range_summary(user_days),
        }
        return record, user_errors

    users, errors = _fan_out(list(ids), fetch_user, concurrency)  # type: ignore[arg-type]

    return {
        "range": {"dates": dr.dates, **make_range_summary([{"date": d} for d in dr.dates])},
        "users": users,
        "errors": errors,
    }


def org_scores_summary(
    *,
    client: SensrClient,
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    days: int | None = None,
    max_users: int = 50,
    concurrency: int = 5,
) -> dict[str, Any]:
    ids = _get_org_user_ids(client, max_users)
    if isinstance(ids, dict) and ids.get("error"):
        return ids

    dr = expand_date_range(date_str=date, start_date=start_date, end_date=end_date, days=days)

    def fetch_user(uid: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        user_days: list[dict[str, Any]] = []
        user_errors: list[dict[str, Any]] = []
        for d in dr.dates:
            try:
                resp = client.request("GET", "/v1/scores", params={"user_id": uid, "date": d})
                user_days.append({"date": d, "data": resp.get("data")})
            except Exception as e:
                user_errors.append(
                    error_dict(
                        message=f"{type(e).__name__}: {e}",
                        endpoint="/v1/scores",
                        method="GET",
                    )
                )
        record = {
            "user_id": uid,
            "days": user_days,
            "summary": make_range_summary(user_days),
        }
        return record, user_errors

    users, errors = _fan_out(list(ids), fetch_user, concurrency)  # type: ignore[arg-type]

    return {
        "range": {"dates": dr.dates, **make_range_summary([{"date": d} for d in dr.dates])},
        "users": users,
        "errors": errors,
    }
