# AI Usage Disclosure

## Tools used

- **DeepSeek Harness** desktop AI coding agent (model: deepseek-flash), used on 2026-11-16.

## Conversation links

- The work was done in a local DeepSeek Harness session. The tool does not provide a public
  share link for conversations; the session was only reachable on the local machine
  (http://127.0.0.1:49966). The full transcript can be provided to the instructor on request.

## What I used them for

- Implementing the four required modules from the assignment specification (validation,
  CSV parsing, queries and the command-line entry point).
- Explaining how argparse reports usage errors and how to clean up the logging handler
  safely when main() is called several times in one process.
- Generating additional edge-case tests and running the public test suite.

## Which parts of the code were AI-generated or substantially AI-assisted

| File | Function or part | How (generated / modified / explained) |
| --- | --- | --- |
| validator.py | load_airports, validate_row, to_record and the regex/date helpers | Generated from the specification, then reviewed |
| csv_loader.py | parse_files (line numbers, comments, duplicate check) | Generated from the specification, then reviewed |
| query.py | run_query, run_queries, query validation and sorting | Generated from the specification, then reviewed |
| flight_parser.py | main, argument parsing, database/response writing, logging setup | Generated from the specification, then reviewed |
| AI_USAGE.md | This disclosure | Drafted with the tool |

## Key prompts

1. "Here is the full Moodle specification for the flight query tool. Implement
   flight_parser.py, validator.py, csv_loader.py and query.py using only the
   Python standard library, keeping the required function signatures."
2. "Run python tests/run_public_tests.py and fix every failing test without editing the
   test files or the expected outputs."
3. "Add edge-case checks for validation order, duplicate flights across files, logging
   handler cleanup when main() runs twice, and invalid query shapes."

## What I changed or verified myself

- The generated code was reviewed and the public test suite was run locally:
  python tests/run_public_tests.py reports all 29 tests passing across groups A-H.
- The sample database, errors.log and query response file were compared with the
  expected outputs in tests/expected/, and the CLI examples from the README were run.
