###################
Public Transit API
###################

Implement functionality in
`NextBus XML Feed <http://www.nextbus.com/xmlFeedDocs/NextBusXMLFeed.pdf>`_.

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
    client.agency_list()

CLI

.. code::

    transit agency list
