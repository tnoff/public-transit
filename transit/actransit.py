import json

import requests

from transit.exceptions import TransitException
from transit.modules.actransit import urls

def route_list(actransit_api_key):
    '''
    List actransit routes

    actransit_api_key   :   Actransit API Key
    '''

    url = urls.route_list(actransit_api_key)
    req = requests.get(url)
    if req.status_code != 200:
        raise TransitException("Non 200 status code returned")

    route_list_data = json.loads(req.text)
    return route_list_data

def route_directions(actransit_api_key, route_name):
    '''
    List route directions

    actransit_api_key   :   Actransit API Key
    route_name          :   Name of route
    '''

    url = urls.route_directions(actransit_api_key, route_name)
    req = requests.get(url)
    if req.status_code != 200:
        raise TransitException("Non 200 status code returned")

    route_dir_data = json.loads(req.text)
    return route_dir_data

def route_trips(actransit_api_key, route_name, direction,
                schedule_type='weekday'):
    '''
    List route trips

    actransit_api_key   :   Actransit API Key
    route_name          :   Name of route
    direction           :   Route direction
    schedule_type       :   Schedule type, either 'weekday', 'saturday', or 'sunday'
    '''

    schedule_type_mapping = {
        'weekday' : 0,
        'saturday' : 5,
        'sunday' : 6,
    }

    if schedule_type not in list(schedule_type_mapping.keys()):
        raise TransitException("Invalid schedule type:%s" % schedule_type)

    url = urls.route_trips(actransit_api_key, route_name, direction,
                           schedule_type_mapping[schedule_type])
    req = requests.get(url)
    if req.status_code != 200:
        raise TransitException("Non 200 status code returned")

    route_trips_data = json.loads(req.text)
    # Output contains schedule type, direction, and route name, which we already know
    for trip in route_trips_data:
        trip.pop('ScheduleType', None)
        trip.pop('RouteName', None)
        trip.pop('Direction', None)
    return route_trips_data

def route_stops(actransit_api_key, route_name, trip_id):
    '''
    List route stops

    actransit_api_key   :   Actransit API Key
    route_name          :   Name of route
    trip_id             :   Trip id
    '''

    url = urls.route_stops(actransit_api_key, route_name, trip_id)
    req = requests.get(url)
    if req.status_code != 200:
        raise TransitException("Non 200 status code returned")

    route_stop_data = json.loads(req.text)
    return route_stop_data

def stop_predictions(actransit_api_key, stop_id):
    '''
    Get stop predictions

    actransit_api_key   :   Actransit API Key
    stop_id             :   Stop Id
    '''
    url = urls.stop_predictions(actransit_api_key, stop_id)
    req = requests.get(url)
    if req.status_code != 200:
        raise TransitException("Non 200 status code returned")

    stop_pred_data = json.loads(req.text)
    # StopId returned in data, remove since we know that already
    for stop in stop_pred_data:
        stop.pop("StopId", None)
    return stop_pred_data

def service_notices(actransit_api_key):
    '''
    Service Notices

    actransit_api_key   :   Actransit API Key
    '''

    url = urls.service_notices(actransit_api_key)
    req = requests.get(url)
    if req.status_code != 200:
        raise TransitException("Non 200 status code returned")

    notices = json.loads(req.text)
    return notices
