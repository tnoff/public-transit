# Development

## Setup

```bash
git clone https://github.com/tnoff/public-transit.git
cd public-transit
pip install -e .
pip install -r requirements.txt
pip install -r tests/requirements.txt
```

## Running Tests

Run the full suite with lint and coverage:

```bash
pylint transit/ trip_planner/
pytest --cov=transit/ --cov=trip_planner/ --cov-fail-under=60 tests/
```

Run a single test file:

```bash
pytest tests/test_bart.py
```

Run a single test:

```bash
pytest tests/test_bart.py::test_station_list
```

## Tox

Tox runs lint and the full test suite across Python 3.11–3.14:

```bash
tox
```

## Architecture

Two top-level packages:

**`transit/`** — thin API client wrappers for each transit system. Each module under `transit/modules/` follows the same pattern: `urls.py` builds URL strings, `client.py` makes HTTP requests via `requests` and returns parsed dicts. CLIs live in `transit/cli/`.

- `transit/modules/bart/` — BART API (JSON). Requires a BART API key per call.
- `transit/modules/actransit/` — AC Transit API (XML parsed via `xmltodict`). Requires an AC Transit API key.
- `transit/modules/nextbus/` — NextBus XML feed. No API key required.

**`trip_planner/`** — higher-level tool built on top of `transit/`. Persists user-defined *Legs* (a stop + filtered destinations) and *Trips* (ordered collections of Legs) in a local SQLite database via SQLAlchemy. The `TripPlanner` class in `trip_planner/client.py` is the main interface; `trip_planner/tables.py` defines the ORM models (`Leg`, `LegDestination`, `Trip`, `TripLeg`). CLI entry point is `trip_planner/cli/planner_script.py`.

## Tests

Tests use `requests_mock` to intercept HTTP calls without hitting live APIs. Fixture data lives in `tests/data/` as Python modules exporting a `DATA` constant. The `pytest` configuration (inside `tox.ini`) treats all warnings as errors.
