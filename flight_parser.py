"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

STUDENT_ID = "241ADB024"
FIRST_NAME = "Zeyi"
LAST_NAME = "Feng"

_LOGGER_NAME = "flight_parser"
_DATETIME_FORMAT = "%Y-%m-%d %H:%M"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flight_parser.py",
        description="Parse and validate flight schedules and answer queries.",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", metavar="FILE", help="parse a single CSV file")
    source.add_argument("-d", metavar="FOLDER", help="parse every .csv file in FOLDER")
    source.add_argument("-j", metavar="FILE", help="load an existing JSON database")
    parser.add_argument("-a", metavar="FILE", help="airport list file (required with -i/-d)")
    parser.add_argument("-o", metavar="FILE", help="output path for the JSON database")
    parser.add_argument("-q", metavar="FILE", help="JSON file with queries to run")
    parser.add_argument("-r", metavar="FOLDER", help="folder for the query response file")
    return parser


def _read_json(path: Path):
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise OSError(f"cannot read {path}: {exc.strerror or exc}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not valid JSON: {exc}") from exc


def _load_database(path: Path) -> list[dict]:
    data = _read_json(path)
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError(f"{path} must contain a JSON array of objects")
    return data


def _load_queries(path: Path):
    data = _read_json(path)
    if isinstance(data, dict):
        return data
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        return data
    raise ValueError(f"{path} must contain a query object or an array of query objects")


def _csv_files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        raise FileNotFoundError(f"folder not found: {folder}")
    paths = sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.name.endswith(".csv")
    )
    if not paths:
        raise FileNotFoundError(f"no .csv files found in {folder}")
    return paths


def _write_database(path: Path, records: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def _write_errors_log(path: Path, errors: list[str]) -> None:
    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    handler = logging.FileHandler(path, mode="w", encoding="utf-8")
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    try:
        logger.addHandler(handler)
        for message in errors:
            logger.warning(message)
    finally:
        logger.removeHandler(handler)
        handler.close()


def _write_response(folder: Path, responses: list[dict]) -> None:
    if not folder.is_dir():
        raise FileNotFoundError(f"folder not found: {folder}")
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    name = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{stamp}.json"
    with open(folder / name, "w", encoding="utf-8") as handle:
        json.dump(responses, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
        if (args.i or args.d) and not args.a:
            parser.error("-a is required when using -i or -d")
        if args.o and args.j:
            parser.error("-o cannot be used with -j")
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 0

    try:
        if args.j:
            db = _load_database(Path(args.j))
        else:
            airports = load_airports(args.a)
            if args.i:
                paths = [Path(args.i)]
            else:
                paths = _csv_files(Path(args.d))
            records, errors = parse_files([str(path) for path in paths], airports)
            db = records
            output = Path(args.o) if args.o else Path.cwd() / "db.json"
            _write_database(output, db)
            _write_errors_log(output.parent / "errors.log", errors)

        if args.q:
            queries = _load_queries(Path(args.q))
            responses = run_queries(db, queries)
            folder = Path(args.r) if args.r else Path.cwd()
            _write_response(folder, responses)
    except Exception as exc:  # expected runtime problems -> clean Error line
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
