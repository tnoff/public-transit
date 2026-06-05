# Development

Setup, tests, and linting for working in this repo. User-facing CLI
and API usage live in [README.md](README.md). For architecture and
non-obvious internals see [AGENTS.md](AGENTS.md).

## Setup

```bash
git clone https://gitlab.com/tnoff-projects/public-transit.git
cd public-transit
pip install -e ".[dev]"
```

## Tests

Full suite (pylint + bandit + pytest with 100% coverage gate) across
py311–py314:

```bash
tox
```

Single Python version:

```bash
tox -e py312
```

Tests only:

```bash
pytest tests/
```

One test file or test:

```bash
pytest tests/test_bart.py
pytest tests/test_bart.py::test_station_list
```

Coverage HTML report:

```bash
pytest --cov=transit/ --cov=trip_planner/ --cov-report=html --cov-fail-under=100 tests/
# open htmlcov/index.html
```

## Linting and security

```bash
pylint transit/ trip_planner/
bandit -r transit/ trip_planner/
```

Both run inside `tox` and must pass for release. `pytest`'s
`filterwarnings = error` (in `tox.ini`) treats every warning as a
test failure.

## Test fixtures

HTTP is intercepted by `requests_mock`. Fixture payloads live under
`tests/data/` as Python modules exporting a `DATA` constant. To add a
new endpoint test, drop a new module there and import it from the
test file — no live API calls.

## Releasing

`VERSION` at the repo root is the source of truth. Bump it and push to
`main` — CI tags the commit and runs the release pipeline via the
shared `tnoff-projects/github-workflows` templates.
