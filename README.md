# HTTP Retry Planner

Compute bounded retry decisions for mock HTTP outcomes, idempotent methods, and attempt limits.

Uses Python 3.10+ and its standard library only. No package installation, virtual
environment, external server, Redis, Celery, or network access is required.

## Run

```console
python -m retries_lab --help
python -m retries_lab examples/sample.json
python -m retries_lab --check-fixtures fixtures/cases.jsonl
python generate_fixtures.py --count 20
python -m unittest discover -s tests -v
```

Run from this directory. The optional path defaults to `-`, which reads JSON from
stdin. Output is JSON or a fixture-check summary. Exit codes are 0 success,
1 file failure, and 2 invalid input. Examples and fixtures contain generated data.

Input describes a mock status (null means connection failure), method, attempt, max_attempts, base_seconds, cap_seconds, optional retry_after seconds, and optional idempotent boolean. This toy policy retries 429, 500, 502, 503, 504, and connection failures. POST/PATCH require caller-declared idempotence. Attempts are one-based; reaching max_attempts stops retries. Exponential backoff is capped, but a supplied retry_after minimum can exceed that cap. It does not parse HTTP-date headers, send requests, implement jitter, or certify a request as idempotent.

## Learning focus

The modeled development of API timeout, retry, failure-handling, and client-policy skills. This is an independent concept exercise based on the modeled
roadmap. It makes no claim to be employer-owned or period-authentic production code.

## Structure

- `retries_lab/core.py`: validated parsing, storage, or state transitions.
- `retries_lab/cli.py`: JSON command interface.
- `retries_lab/generate_fixtures.py`: original deterministic validation cases.
- `retries_lab/fixture_check.py`: expected-output/error checks.
- `fixtures/cases.jsonl`: 434 generated cases, with explicit descriptions.
- `tests/`: independently selected boundaries and the complete corpus check.

Branches `feature/core`, `feature/cli`, `data/fixtures`, and `docs/usage` retain
snapshots; `main` contains the complete tool. Dates and provenance are also recorded
in TIMELINE.json. Many data cases share a scenario; they are not separate features.

Keep changes focused, use actual dates for new work, and add a regression test
for changed behavior. Licensed under [MIT](LICENSE).

[History and provenance](HISTORY.md).
