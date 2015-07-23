###################
Public Transit API
###################

Implement functionality in

- `NextBus XML Feed <http://www.nextbus.com/xmlFeedDocs/NextBusXMLFeed.pdf>`_

- `BART API <http://api.bart.gov/docs/overview/index.aspx>`_

========================
Functionality Checklist
========================

-------
NextBus
-------

#. Agency List -- Done
#. Agency Route List -- Done
#. Agency Route Config -- Done
#. Stop Predictions -- Done

    - Just stop, no route -- Done
    - Stop and route -- Done

#. Multiple Stop Prediction -- Done
#. Agency Route Schedule -- Done
#. Agency Route Messages -- Done
#. Agency Route Vehicle Locations -- Done

----
BART
----

#. Advisories -- Done
#. Real-Time Estimates -- Done
#. Route Information -- Done
#. Schedule Information
#. Station Information -- Done

=======
Install
=======

.. code::

    git clone git@github.com:tylernorth/public-transit.git
    pip install public-transit/

=====
Usage
=====
API

.. code::

    from transit import client
    client.nextbus.agency_list()
    client.bart.train_count()

CLI

.. code::

    nextbus agency list
    bart service-advisory


============
Trip Planner
============
Trip planner was a wrapper I created to quickly show multiple routes from
different agencies.

Example::

    # trip-planner leg list
    +--------+-----------+---------+----------+-----------------------------+-------------------+
    | Leg ID |   Agency  | Stop ID | Stop Tag |          Stop Title         | Routes/Directions |
    +--------+-----------+---------+----------+-----------------------------+-------------------+
    |   1    | actransit |  51303  | 9902820  | Mission Blvd & Central Blvd |    22, 99, 801    |
    |   2    |    bart   |   hayw  |   None   |           Hayward           |     daly, dubl    |
    |   3    |    bart   |   bayf  |   None   |    Bay Fair (San Leandro)   |        daly       |
    |   4    |    bart   |   mont  |   None   |     Montgomery St. (SF)     |     frmt, dubl    |
    |   5    | actransit |  55911  | 0802060  |     Hayward BART Station    |         22        |
    |   6    | actransit |  55532  | 0802020  |     Hayward BART Station    |      99, 801      |
    |   7    |    bart   |   bayf  |   None   |    Bay Fair (San Leandro)   |        frmt       |
    |   8    | actransit |  53520  | 1504230  |     Bayfair BART Station    |         99        |
    +--------+-----------+---------+----------+-----------------------------+-------------------+
    # trip-planner trip list
    +----+--------------+---------------+
    | ID |     Name     |      Legs     |
    +----+--------------+---------------+
    | 1  | home-to-work |    1, 2, 3    |
    | 2  | work-to-home | 4, 7, 5, 6, 8 |
    +----+--------------+---------------+
    # trip-planner trip show 1
    Bart data
    +----------+-----------+--------------------+
    | Station  | Direction | Estimates(minutes) |
    +----------+-----------+--------------------+
    | Bay Fair | Daly City |    2 ; 11 ; 17     |
    | Hayward  | Daly City |    8 ; 22 ; 37     |
    +----------+-----------+--------------------+
    Nextbus Agency:actransit
    +-------+-----------------------------+----------------------------------+---------------------------------------+
    | Route |          Stop Title         |            Direction             |              Predictions              |
    +-------+-----------------------------+----------------------------------+---------------------------------------+
    |   99  | Mission Blvd & Central Blvd |         To Bay Fair BART         | 02:12 ; 29:45 ; 44:01 ; 69:24 ; 87:20 |
    |   22  | Mission Blvd & Central Blvd | Counterclockwise to Hayward BART |         12:50 ; 43:00 ; 72:46         |
    +-------+-----------------------------+----------------------------------+---------------------------------------+
