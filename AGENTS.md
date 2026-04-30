# AGENTS.md

This file provides guidance to AI agents when working with code in this repository.

## Commands

Install the package and dependencies:
```bash
pip install -e ".[dev]"
```

Run lint and all tests (as tox does):
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

Run via tox (tests Python 3.11–3.14):
```bash
tox
```

## Architecture

This repo contains two top-level Python packages:

**`transit/`** — thin API client wrappers for three transit systems:
- `transit/modules/bart/` — BART API (JSON). Requires a BART API key passed per-call.
- `transit/modules/actransit/` — AC Transit API (XML via `xmltodict`/`beautifulsoup4`). Requires an AC Transit API key.
- `transit/modules/nextbus/` — NextBus XML feed. No API key required.

Each module follows the same pattern: `urls.py` builds URL strings, `client.py` calls those URLs via `requests` and returns parsed dicts. CLIs live in `transit/cli/`.

**`trip_planner/`** — a higher-level tool built on top of `transit/`. It persists user-defined *Legs* (a stop + filtered destinations) and *Trips* (ordered collections of Legs) in a local SQLite database via SQLAlchemy. The `TripPlanner` class in `trip_planner/client.py` is the main interface; `trip_planner/tables.py` defines the ORM models (`Leg`, `LegDestination`, `Trip`, `TripLeg`). The CLI entry point is `trip_planner/cli/planner_script.py`.

**Tests** use `requests_mock` to intercept HTTP calls. Fixture data lives in `tests/data/` as Python modules exporting a `DATA` dict. `pytest.ini` options (inside `tox.ini`) treat warnings as errors.
