# AGENTS.md

Guidance for AI coding agents working in this repository. For end-user
CLI and Python API see [README.md](README.md); for setup, tests, and
linting see [DEVELOPMENT.md](DEVELOPMENT.md).

## Architecture

Two top-level Python packages:

### `transit/` — thin API wrappers

Three transit-system modules under `transit/modules/`, each following
the same shape:

| Module | Wire format | API key |
|---|---|---|
| `transit/modules/bart/` | JSON | required per call |
| `transit/modules/actransit/` | XML (`xmltodict`) | required per call |
| `transit/modules/nextbus/` | XML | not required |

Each module has `urls.py` (URL builders) and `client.py` (HTTP via
`requests`, returns parsed dicts). CLIs live in `transit/cli/` and
register the per-system `bart`, `actransit`, `nextbus` entry points.

### `trip_planner/`

Higher-level tool built on top of `transit/`. Persists user-defined
**Legs** (a stop + filtered destinations) and **Trips** (ordered
collections of Legs) in a SQLite DB via SQLAlchemy.

- `trip_planner/client.py` — `TripPlanner` class, the main interface
- `trip_planner/tables.py` — ORM models (`Leg`, `LegDestination`,
  `Trip`, `TripLeg`)
- `trip_planner/cli/planner_script.py` — `trip-planner` entry point

## Non-obvious internals

### API keys are passed per call, not held in state

Every BART / AC Transit client function takes `api_key` as its first
argument. There is no module-level config or `Client` object that
holds it. This is deliberate — it makes the wrappers trivial to use
from notebooks, lets callers rotate keys without re-initialising, and
keeps the test suite stateless. Don't introduce a session-style
client that holds the key.

### XML parsing differs between AC Transit and NextBus

AC Transit uses `xmltodict` to round-trip the entire XML response to
a dict. NextBus uses `beautifulsoup4` because its XML is sloppier and
`xmltodict` chokes on the inconsistent attribute styles. If you add a
new XML-format source, check the upstream payload before picking the
parser — `xmltodict` is preferable when it works.

### `pytest filterwarnings = error`

`tox.ini` sets `filterwarnings = error` under `[pytest]`. Any
`DeprecationWarning` from a dependency surfaces as a test failure.
When bumping a dep that emits new deprecations, either silence the
specific warning in `filterwarnings` with a `ignore::Warning:<module>`
entry (preferred — keeps the gate on for everything else) or fix the
usage.

### `requests_mock` everywhere — no live API hits in tests

All HTTP is intercepted by `requests_mock`. Fixture payloads live under
`tests/data/` as Python modules that export a `DATA` constant
(matching the upstream API's shape exactly). The test suite never
hits the live APIs, both for repeatability and because some are
rate-limited.

### Trip Planner `destinations` filter is agency-specific

The `destinations` field on a Leg means different things per agency:

- BART — terminal-station abbreviations (`DUBL`, `FRMT`)
- NextBus — route tags (`38` for sf-muni 38-Geary)

There is no unified taxonomy. If you add another agency, document
what `destinations` means for it in the CLI help and in
[README.md](README.md#trip-planner).

### Coverage gate is **100%**

`tox.ini` runs `pytest --cov-fail-under=100`. The old AGENTS doc
claimed 60% — that's stale. New code paths need exhaustive tests.

## Conventions

- New transit module under `transit/modules/<name>/` follows the
  `urls.py` + `client.py` pair. CLI entry in `transit/cli/<name>.py`,
  registered in `pyproject.toml [project.scripts]`.
- API keys flow per-call as the first argument.
- New `trip_planner` features go through `TripPlanner` in `client.py`,
  not directly via the ORM models.
