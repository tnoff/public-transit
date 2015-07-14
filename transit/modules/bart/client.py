from transit.modules.bart import advisories as advisory_client
from transit.modules.bart import routes as route_client
from transit.modules.bart import schedules as schedule_client
from transit.modules.bart import stations as station_client

def service_advisory():
    '''Bart Service Advisory (For All Stations)'''
    return advisory_client.service_advisory()

def train_count():
    '''Current number of Bart Trains'''
    return advisory_client.train_count()

def elevator_status():
    '''Elevator Status for all stations'''
    return advisory_client.elevator_status()

def route_list(schedule=None, date=None):
    '''List of current routes
       schedule: schedule number
       date: mm/dd/yyyy format
    '''
    return route_client.route_list(schedule=schedule, date=date)

def route_show(route_number, schedule=None, date=None):
    '''Show information for specific route
       route_number: number of route to show
       schedule: schedule number
       date: mm/dd/yyyy format
    '''
    return route_client.route_show(route_number, schedule=schedule,
                                   date=date)

def station_list():
    '''List of stations'''
    return station_client.station_list()

def station_info(station):
    '''Get station info
       station: station abbreviation
    '''
    return station_client.station_info(station)

def station_access(station):
    '''Access information for station
       station: station abbreviation
    '''
    return station_client.station_access(station)

def station_departures(station, platform=None, direction=None):
    '''Get estimated station departures
       station: station abbreviation
       plaform: platfrom number
       direction: (n)orth or (s)outh
    '''
    return station_client.station_departures(station, platform=platform,
                                             direction=direction)

def station_schedule(station, date=None):
    '''Get a stations schedule
       station: station abbreviation
       date: mm/dd/yyyy format
    '''
    return station_client.station_schedule(station, date=date)

def schedule_list():
    '''Get a list of current schedules'''
    return schedule_client.schedule_list()

def schedule_fare(origin_station, destination_station,
                  date=None, schedule=None):
    return schedule_client.schedule_fare(origin_station,
                                         destination_station,
                                         date=date,
                                         schedule=schedule)
