import requests

from transit.exceptions import TransitException
from transit.modules.actransit import urls

def _make_request(url):
    req = requests.get(url)
    if req.status_code != 200:
        raise TransitException(f'Non 200 status code {req.status_code} returned, "{req.text}"')
    return req.json()

def route_list(actransit_api_key):
    '''
    List actransit routes

    actransit_api_key   :   Actransit API Key
    '''
    url = urls.route_list(actransit_api_key)
    return _make_request(url)

def route_directions(actransit_api_key, route_name):
    '''
    List route directions

    actransit_api_key   :   Actransit API Key
    route_name          :   Name of route
    '''
    url = urls.route_directions(actransit_api_key, route_name)
    return _make_request(url)

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
        raise TransitException(f'Invalid schedule type: "{schedule_type}"')

    url = urls.route_trips(actransit_api_key, route_name, direction,
                           schedule_type_mapping[schedule_type])
    return _make_request(url)

def route_stops(actransit_api_key, route_name, trip_id):
    '''
    List route stops

    actransit_api_key   :   Actransit API Key
    route_name          :   Name of route
    trip_id             :   Trip id
    '''
    url = urls.route_stops(actransit_api_key, route_name, trip_id)
    return _make_request(url)

def stop_predictions(actransit_api_key, stop_ids, route_names=None):
    '''
    Get stop predictions

    actransit_api_key   :   Actransit API Key
    stop_ids            :   Stop Ids
    route_names         :   Only show specific routes
    '''
    url = urls.stop_predictions(actransit_api_key, stop_ids, route_names)
    return _make_request(url)


def service_notices(actransit_api_key):
    '''
    Service Notices

    actransit_api_key   :   Actransit API Key
    '''
    url = urls.service_notices(actransit_api_key)
    return _make_request(url)
