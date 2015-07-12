from transit.modules.bart import advisories as advisory_client
from transit.modules.bart import estimates as estimate_client
from transit.modules.bart import routes as route_client
from transit.modules.bart import stations as station_client

def service_advisory():
    return advisory_client.service_advisory()

def train_count():
    return advisory_client.train_count()

def elevator_status():
    return advisory_client.elevator_status()

def estimated_departures(station, platform=None, direction=None):
    return estimate_client.estimated_departures(station, platform=platform,
                                                direction=direction)

def current_routes(schedule=None, date=None):
    return route_client.current_routes(schedule=schedule, date=date)

def route_info(route_number, schedule=None, date=None):
    return route_client.route_info(route_number, schedule=schedule,
                                   date=date)

def station_list():
    return station_client.station_list()

def station_info(station):
    return station_client.station_info(station)

def station_access(station, legend=False):
    return station_client.station_access(station, legend=legend)
