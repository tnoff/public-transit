# Public Transit API

Python library and CLI tools for Bay Area transit APIs:

- [BART API](http://api.bart.gov/docs/overview/index.aspx)
- [AC Transit API](https://www.actransit.org/data-api-resource-center)
- [NextBus XML Feed](http://www.nextbus.com/xmlFeedDocs/NextBusXMLFeed.pdf)
- [511.org Open Data API](https://511.org/open-data/transit) — real-time
  departures for ~30 Bay Area operators (VTA, SF Muni, Caltrain, SamTrans,
  Golden Gate, …) through one SIRI feed

## Install

```bash
git clone https://gitlab.com/tnoff-projects/public-transit.git
pip install public-transit/
```

## Docker

If you'd rather not set up a local Python environment, you can build and run with Docker:

```bash
git clone https://gitlab.com/tnoff-projects/public-transit.git
cd public-transit
docker build -t public-transit .
```

Then run any of the CLI commands:

```bash
docker run --rm public-transit bart --help
docker run --rm public-transit actransit --help
docker run --rm public-transit nextbus agency-list
```

For `trip-planner`, mount a local directory so the SQLite database persists between runs:

```bash
docker run --rm -v "$HOME/.trip_planner:/root/.trip_planner" public-transit trip-planner leg-list
```

## CLI Scripts

Installing the package provides five commands:

| Command | Description |
|---|---|
| `bart` | BART station departures, advisories, and train info |
| `actransit` | AC Transit routes, trips, and stop predictions |
| `nextbus` | NextBus agency, route, and stop predictions |
| `five11` | 511.org operators, lines, stops, and real-time departures (VTA, Muni, Caltrain, …) |
| `trip-planner` | Save and query common routes across all agencies |

Run any command with `--help` for full usage details, e.g. `bart --help`.

## Python API

Each transit module exposes standalone functions. Import from the relevant client module:

```python
from transit.modules.bart import client as bart

# Requires a BART API key (public demo key: MW9S-E7SL-26DU-VV8V)
departures = bart.station_departures('MW9S-E7SL-26DU-VV8V', 'MONT')
stations = bart.station_list('MW9S-E7SL-26DU-VV8V')
```

```python
from transit.modules.actransit import client as actransit

# Requires an AC Transit API key
predictions = actransit.stop_predictions(api_key, '51303')
```

```python
from transit.modules.nextbus import client as nextbus

# No API key required
agencies = nextbus.agency_list()
predictions = nextbus.stop_prediction('sf-muni', '15684')
```

```python
from transit.modules.five11 import client as five11

# Requires a 511.org API key; operator id 'SC' is Santa Clara VTA
operators = five11.operators(api_key)          # discover operator ids
lines = five11.lines(api_key, 'SC')            # discover line ids (routes)
stops = five11.stops(api_key, 'SC')            # all stops for the operator
line_22_stops = five11.stops(api_key, 'SC', line_id='22')  # stops on one line
response = five11.stop_monitoring(api_key, 'SC', '70021')
departures = five11.stop_visits(response)  # flat list of stop/line/destination/arrival
```

## Trip Planner

Trip planner lets you save frequently used stops and destinations to a local SQLite database, then query them all at once.

A **leg** is a stop at a specific agency, optionally filtered to certain destinations. A **trip** is an ordered collection of legs.

```bash
# Create a leg: BART Montgomery St., filtering to Fremont-bound trains
$ trip-planner leg-create bart mont --destinations frmt
{
    "stop_id": "mont",
    "stop_title": "Montgomery St.",
    "agency": "bart",
    "stop_tag": null,
    "includes": [
        "frmt"
    ]
}

# Show live departure times for all legs in a saved trip
# (times render as H:MM:SS / M:SS / seconds)
$ trip-planner trip-show 2
Agency bart
Stop                    || Destination                       || Times (H:MM:SS)
-------------------------------------------------------------------------------
Concord                 || SF Airport                        || 44:00
```

Multi-agency providers use a `provider:agency` tag; single-agency
modules (`bart`, `actransit`) are bare:

- **511** (VTA, Muni, Caltrain, …) → `511:<OPERATOR>`, where the operator
  id comes from `five11 operators` (e.g. `SC` for Santa Clara VTA)
- **NextBus** → `nextbus:<AGENCY>` (e.g. `nextbus:sf-muni`)

An unknown or unprefixed tag is rejected with a hint, so a typo can't
silently be treated as a NextBus agency.

```bash
# Create a leg: VTA (operator SC) stop 70021, filtering to the 22 line
$ trip-planner leg-create 511:SC 70021 --destinations 22

# NextBus: the sf-muni 38-Geary stop
$ trip-planner leg-create nextbus:sf-muni 5684 --destinations 38
```

The `destinations` filter corresponds to:
- The terminal station abbreviation for BART routes (e.g. `DUBL`, `FRMT`)
- The route tag for NextBus stops (e.g. `38` for the 38-Geary on sf-muni)
- The line ref for 511 operators (e.g. `22` or `522` for VTA)

Run `trip-planner --help` for the full list of commands.
