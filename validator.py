"""Row validation: airport list loading, single-row checks, record building."""
import math
import re
from datetime import datetime

_FLIGHT_ID_RE = re.compile(r"^[A-Za-z0-9]{2,8}$")
_AIRPORT_RE = re.compile(r"^[A-Z]{3}$")
_DATETIME_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}$")


def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes.

    One code per line. Strip whitespace; skip blank lines and lines
    starting with '#'.
    """
    airports: set[str] = set()
    with open(path, encoding="utf-8-sig") as handle:
        for line in handle:
            code = line.strip()
            if not code or code.startswith("#"):
                continue
            airports.add(code)
    return airports


def _parse_datetime(value: str) -> datetime | None:
    """Parse an exact 'YYYY-MM-DD HH:MM' value, or return None."""
    if not _DATETIME_RE.match(value):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError:
        return None


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Check one CSV row (fields as returned by csv.reader, not yet stripped).

    Return None if the row is valid, otherwise the error code of the
    FIRST failing check (checks 1-11 in the specification, in order).
    Does not check for duplicates.
    """
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    values = [field.strip() for field in fields]
    if any(value == "" for value in values):
        return "MISSING_FIELD"

    flight_id, origin, destination, departure, arrival, price_text = values

    if not _FLIGHT_ID_RE.match(flight_id):
        return "INVALID_FLIGHT_ID"
    if not _AIRPORT_RE.match(origin) or origin not in airports:
        return "INVALID_ORIGIN"
    if not _AIRPORT_RE.match(destination) or destination not in airports:
        return "INVALID_DESTINATION"
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    departure_dt = _parse_datetime(departure)
    if departure_dt is None:
        return "INVALID_DEPARTURE"

    arrival_dt = _parse_datetime(arrival)
    if arrival_dt is None:
        return "INVALID_ARRIVAL"

    if arrival_dt <= departure_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        price = float(price_text)
    except ValueError:
        return "INVALID_PRICE"
    if not math.isfinite(price):
        return "INVALID_PRICE"
    if price <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary.

    Keys: flight_id, origin, destination, departure_datetime,
    arrival_datetime (stripped strings) and price (float).
    """
    values = [field.strip() for field in fields]
    return {
        "flight_id": values[0],
        "origin": values[1],
        "destination": values[2],
        "departure_datetime": values[3],
        "arrival_datetime": values[4],
        "price": float(values[5]),
    }
