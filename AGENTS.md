# AGENTS.md

Guidance for AI coding agents working in this repository. For end-user
CLI and Python API see [README.md](README.md); for setup, tests, and
linting see [DEVELOPMENT.md](DEVELOPMENT.md).

## Architecture

Two top-level Python packages:

### `transit/` — thin API wrappers

Transit-system modules under `transit/modules/`, each following the
same shape:

| Module | Wire format | API key |
|---|---|---|
| `transit/modules/bart/` | JSON | required per call |
| `transit/modules/actransit/` | JSON (`.json()`) | required per call |
| `transit/modules/nextbus/` | XML (`xmltodict`) | not required |
| `transit/modules/five11/` | JSON (SIRI) | required per call |

Each module has `urls.py` (URL builders) and `client.py` (HTTP via
`requests`, returns parsed dicts). CLIs live in `transit/cli/` and
register the per-system `bart`, `actransit`, `nextbus`, `five11` entry
points.

`five11` is generic over the 511.org operator id (`SC`=VTA, `SF`=Muni,
`CT`=Caltrain, …), the same way `nextbus` is generic over its agency
tag. In the trip planner these multi-agency providers use a
`provider:agency` tag — `511:<operator>` and `nextbus:<agency>` — while
the single-agency modules (`bart`, `actransit`) are bare. An unknown or
unprefixed tag is rejected at `leg_create` (no silent NextBus
fall-through).

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

### Wire formats differ between modules

BART, AC Transit, and 511 all return JSON (parsed with `requests`'
`.json()`). Only NextBus returns XML, parsed with `xmltodict`
(`postprocessor` strips the leading `@` off attribute keys). If you add
a new XML-format source, check the upstream payload before picking the
parser — `xmltodict` is preferable when it works. Note: 511 prefixes
its JSON with a UTF-8 BOM, so `five11.client` sets
`req.encoding = 'utf-8-sig'` before `.json()`.

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
- NextBus (`nextbus:<agency>`) — route tags (`38` for sf-muni 38-Geary)
- 511 (`511:<operator>`) — line refs (`22`, `522` for VTA)

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
