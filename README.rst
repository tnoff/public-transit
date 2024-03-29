###################
Public Transit API
###################

Implements functionality in

- `NextBus XML Feed <http://www.nextbus.com/xmlFeedDocs/NextBusXMLFeed.pdf>`_
- `BART API <http://api.bart.gov/docs/overview/index.aspx>`_
- `AC Transit API <https://www.actransit.org/data-api-resource-center>`_

=======
Install
=======

.. code::

    git clone https://github.com/tnoff/public-transit.git
    pip install public-transit/

====================
Command Line Scripts
====================
There will be 4 command line scripts installed:

- actransit
- bart
- nextbus
- trip-planner

Actransit, Bart, and Nextbus are used for actions specific to their APIs.
Trip planner is a wrapper I created to track common routes and easily display them.

All of the CLIs have man pages that detail their use.

=========
API Usage
=========
You can use the API for bart and nextbus data as well.

---------
Actransit
---------
From the help page.

.. code::
    >>> import transit
    >>> help(transit.actransit)

----
Bart
----
From the help page.

.. code::

    >>> import transit
    >>> help(transit.bart)
-------
Nextbus
-------
From the help page.

.. code::

    >>> import transit
    >>> help(transit.nextbus)

============
Trip Planner
============
Trip planner was a small tool I wrote after realizing 99% of the time I use these APIs, I'm
looking up the same stops/routes. Trip planner will let you create routes that will be stored
in a databse, that can be easily retrieved and used.

Heres a brief example of how it's used::

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
    $ trip-planner trip-show 2
    Agency bart
    Stop                     | Destination              | Times (Seconds)
    --------------------------------------------------------------------------------
    Concord                  | SF Airport               | 2640
    ================================================================================

The CLI for Trip planner has a man page that can explain more of the functionality.

One note: The 'destinations' specified when creating a leg correspond to:

- The last station of the bart route, such as "DUBL" (dublin/pleasenton) or "FRMT" (fremont)
- The route you will board at the nextbus stop, such as the "M" Line on sf-muni.


=====
Tests
=====
Tests require extra pip modules to be installed, they reside in the ``tests/requirements.txt`` file.
