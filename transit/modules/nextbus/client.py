'''NextBus API Client
Gather all information using methods
'''
from transit.modules.nextbus import agency, route, stop, schedule, vehicle

def agency_list():
    '''Get list of all agencies'''
    return agency.list_all()

def route_list(agency_tag):
    '''Get list of routes for agency
       agency_tag: agency tag
    '''
    return route.route_list(agency_tag)

def route_get(agency_tag, route_tag):
    '''Get information about specific route
       agency_tag: agency_tag
       route_tag: route_tag
    '''
    return route.route_get(agency_tag, route_tag)

def stop_prediction(agency_tag, stop_id, route_tags=None):
    '''Get arrival predictions for stops
       agency_tag: agency tag
       stop_id: stop id
       route_tags: list of routes to show, enter single value to search directly
    '''
    return stop.stop_prediction(agency_tag, stop_id, route_tags=route_tags)

def multiple_stop_predictions(agency_tag, stop_data):
    '''Get predictions for multiple stops
       agency_tag: agency tag
       stop_data:{route_tag : [stoptag, stoptag, ..], ...}
    '''
    return stop.multiple_stop_prediction(agency_tag, stop_data)

def schedule_get(agency_tag, route_tag):
    '''Get information for route schedule
       agency_tag: agency_tag
       route_tag: route_tag
    '''
    return schedule.schedule_get(agency_tag, route_tag)

def vehicle_location(agency_tag, route_tag, epoch_time):
    '''Get vehicle location for route at time
       agency_tag: agency_tag
       route_tag: route_tag
       epoch_time: epoch time for locations
    '''
    return vehicle.vehicle_location(agency_tag, route_tag, epoch_time)

def message_get(agency_tag, route_tags):
    '''Get system message for routes
       agency_tag: agency_tag
       route_tag: route_tag
    '''
    return route.message_get(agency_tag, route_tags)
