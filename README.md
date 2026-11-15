# Flight Schedule Parser and Query Tool

RTU Programming Languages (Python) - graded lab.

The program validates flight schedule CSV files, stores the valid flights in a JSON
database, writes invalid rows to `errors.log`, and answers queries against the database.

Student: Zeyi Feng (241ADB024)

## Files

| File | Purpose |
| --- | --- |
| `flight_parser.py` | Command-line entry point (`main`), argument parsing, output files |
| `validator.py` | Airport list loading, row validation, record building |
| `csv_loader.py` | Reads CSV files and performs the duplicate check |
| `query.py` | Query validation, filtering and sorting |
| `data/` | Sample CSV files, airport list and queries |
| `tests/` | Public test script and expected outputs |

## Usage

```bash
python flight_parser.py -i data/db.csv -a data/airports.txt
python flight_parser.py -d data/flights -a data/airports.txt -o out/db.json
python flight_parser.py -j out/db.json -q data/query.json -r out/
python flight_parser.py -i data/db.csv -a data/airports.txt -q data/query.json
```

Only the Python standard library is used.

## Tests

```bash
python tests/run_public_tests.py
```

All 29 public tests pass (groups A-H).
