'''Public Transit Client
Modules: nextbus and bart
'''
from transit.modules.bart import client as bart_client
from transit.modules.nextbus import client as nextbus_client

nextbus = nextbus_client
bart = bart_client
