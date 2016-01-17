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

    git clone git@github.com:tylernorth/public-transit.git
    pip install public-transit/

=====
Usage
=====
API

.. code::

    from transit.modules.bart import client as bart_client
    from transit.modules.nextbus import client as nextbus_client

    nextbus_client.agency_list()
    bart_client.train_count()

    # to see all possible functions
    help(bart_client)
    help(nextbus_client)

CLI

.. code::

    nextbus agency list
    bart service advisory
