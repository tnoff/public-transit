###################
Public Transit API
###################

Implements functionality in

- `NextBus XML Feed <http://www.nextbus.com/xmlFeedDocs/NextBusXMLFeed.pdf>`_

- `BART API <http://api.bart.gov/docs/overview/index.aspx>`_

=======
Install
=======

.. code::

    git clone https://github.com/tnoff/public-transit.git
    pip install public-transit/

====================
Command Line Scripts
====================
There will be 3 command line scripts installed:

- bart
- nextbus
- trip-planner

Bart and Nextbus are used for actions specific to their APIs.
Trip planner is a wrapper I created to track common routes and easily display them.

All of the CLIs have man pages that detail their use.

=========
API Usage
=========
You can use the API for bart and nextbus data as well.

----
Bart
----
From the help page.

.. code::

    >>> help(transit.bart)

    elevator_status()
        System wide elevator status

    route_info(route_number, schedule=None, date=None)
        Show information for specific route
        route_number: number of route to show
        schedule: schedule number
        date: mm/dd/yyyy format

    route_list(schedule=None, date=None)
        Show information for specific route
        schedule: schedule number
        date: mm/dd/yyyy format

    schedule_fare(origin_station, destination_station, date=None, schedule=None)
        Get the scheduled fare
        origin_station: station you'll onbard at
        destination_station: station you'll offboard at
        schedule: schedule number
        date: mm/dd/yyyy format

    schedule_list()
        List bart schedules

    service_advisory()
        System wide service advisory

    station_access(station)
        Station Access information
        station: station abbreviation

    station_departures(station, platform=None, direction=None, destinations=None)
        Get estimated station departures
        station: station abbreviation
        plaform: platfrom number
        direction: (n)orth or (s)outh
        destinatons: List of abbreviated destinations, exclude all others

    station_info(station)
        Station information
        station: station abbreviation

    station_list()
        List all bart stations

    station_multiple_departures(station_output)
        Get estimated departures for mutliple stations
        station_output:
            {
                'station_abbrevation' : [destination1, destination2],
                'station_abbreviation2' : [],
                # empty for all possible destinations
            }

    station_schedule(station, date=None)
        Get a stations schedule
        station: station abbreviation
        date: mm/dd/yyyy format

    train_count()
        System wide train count

-------
Nextbus
-------
From the help page.

.. code::

    >>> help(transit.nextbus)

    agency_list()
        List all nextbus agencies

    route_show(agency_tag, route_tag)
        Get information about route
        agency_tag: agency tag
        route_tag : route_tag

    route_list(agency_tag)
        Get list of agency routes
        agency_tag: agency tag

    route_messages(agency_tag, route_tags)
        Get alert messages for routes
        agency_tag : agency tag
        route_tags : either single route tag, or list of tags

    schedule_get(agency_tag, route_tag)
        Get schedule information for route
        agency_tag : agency tag
        route_tag : route tag

    stop_multiple_predictions(agency_tag, prediction_data)
        Get predictions for multiple stops
        agency_tag: agency tag
        prediction_data : {
             "stop_tag1" : [route1, route2],
             "stop_tag2" : [route3],
             # must provide at least one route per stop tag
        }

    stop_prediction(agency_tag, stop_id, route_tags=None)
        Get arrival predictions for stops
        agency_tag: agency tag
        stop_id: stop id
        route_tags: list of routes or single route to limit search

    vehicle_location(agency_tag, route_tag, epoch_time)
        Get vehicle location for route at time
        agency_tag: agency tag
        route_tag: route tag
        epoch_time: epoch time for locations

============
Trip Planner
============
Trip planner was a small tool I wrote after realizing 99% of the time I use these APIs, I'm
looking up the same stops/routes. Trip planner will let you create routes that will be stored
in a databse, that can be easily retrieved and used.

Heres a brief example of how it's used::

    >trip-planner leg create bart mont --destinations frmt
    New leg created: 8
    >trip-planner trip create 'montgomery bart' 8
    Trip created:5
    >trip-planner trip show 5
    Bart
    +----------------+-----------+--------------------+
    |    Station     | Direction | Estimates(minutes) |
    +----------------+-----------+--------------------+
    | Montgomery St. |  Fremont  |    14 ; 29 ; 44    |
    +----------------+-----------+--------------------+

The CLI for Trip planner has a man page that can explain more of the functionality.

One note: The 'destinations' specified when creating a leg correspond to:

- The last station of the bart route, such as "DUBL" (dublin/pleasenton) or "FRMT" (fremont)
- The route you will board at the nextbus stop, such as the "M" Line on sf-muni.


=====
Tests
=====
Tests require extra pip modules to be installed, they reside in the ``tests/requirements.txt`` file.


======
TODOs
======

- Move scripts into each folder

- Change asserts so they throw custom exception

- Allow multi-delete in trip planner

- Fix tests to trip planner

- Allow specifying of custom api keys
