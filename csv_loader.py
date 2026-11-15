"""Reading CSV files into flight records and error messages."""
import csv
from pathlib import Path

from validator import to_record, validate_row


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given.

    Return (records, errors):
      records - valid flight records, in input order
      errors  - one message per invalid row, in input order, formatted as
                "<file name>:<line number>: <ERROR_CODE> | <free text>"
                (base file name only, no timestamp or level, no newline)

    Also performs the DUPLICATE_FLIGHT check across all the files.
    Does not write any files and does not log anything itself.
    """
    records: list[dict] = []
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()

    for file_path in paths:
        path = Path(file_path)
        with open(path, encoding="utf-8-sig", newline="") as handle:
            for line_number, raw_line in enumerate(handle, 1):
                # Line 1 is always the header and is never validated.
                if line_number == 1:
                    continue

                line = raw_line.rstrip("\r\n")
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue

                fields = next(csv.reader([line]), [])
                code = validate_row(fields, airports)

                if code is None:
                    key = (fields[0].strip(), fields[3].strip())
                    if key in seen:
                        code = "DUPLICATE_FLIGHT"
                    else:
                        seen.add(key)
                        records.append(to_record(fields))

                if code is not None:
                    errors.append(f"{path.name}:{line_number}: {code} | {stripped}")

    return records, errors
