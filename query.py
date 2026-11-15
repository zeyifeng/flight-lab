"""Running queries against the flight database."""
import re
from datetime import datetime

_RECORD_KEYS = (
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price",
)
_STRING_KEYS = {"flight_id", "origin", "destination"}
_DATETIME_KEYS = {"departure_datetime", "arrival_datetime"}
_NUMBER_KEYS = {"price", "min_price"}
_ALLOWED_KEYS = _STRING_KEYS | _DATETIME_KEYS | _NUMBER_KEYS | {"sort_by", "order", "limit"}
_DATETIME_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}$")


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_datetime(value) -> bool:
    if not isinstance(value, str) or not _DATETIME_RE.match(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError:
        return False
    return True


def _is_valid_query(query) -> bool:
    if not isinstance(query, dict):
        return False
    if any(key not in _ALLOWED_KEYS for key in query):
        return False

    for key, value in query.items():
        if key in _STRING_KEYS:
            if not isinstance(value, str):
                return False
        elif key in _DATETIME_KEYS:
            if not _is_datetime(value):
                return False
        elif key in _NUMBER_KEYS:
            if not _is_number(value):
                return False
        elif key == "limit":
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                return False
        elif key == "sort_by":
            if value not in _RECORD_KEYS:
                return False
        elif key == "order":
            if value not in ("asc", "desc"):
                return False

    if "order" in query and "sort_by" not in query:
        return False
    return True


def _matches(flight: dict, query: dict) -> bool:
    for key in ("flight_id", "origin", "destination"):
        if key in query and flight[key] != query[key]:
            return False
    if "departure_datetime" in query and flight["departure_datetime"] < query["departure_datetime"]:
        return False
    if "arrival_datetime" in query and flight["arrival_datetime"] > query["arrival_datetime"]:
        return False
    if "price" in query and not flight["price"] <= query["price"]:
        return False
    if "min_price" in query and not flight["price"] >= query["min_price"]:
        return False
    return True


def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    if not _is_valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = [flight for flight in db if _matches(flight, query)]

    if "sort_by" in query:
        key = query["sort_by"]
        reverse = query.get("order", "asc") == "desc"
        matches.sort(key=lambda flight: flight[key], reverse=reverse)

    if "limit" in query:
        matches = matches[: query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    if isinstance(queries, dict):
        return [run_query(db, queries)]
    return [run_query(db, item) for item in queries]
