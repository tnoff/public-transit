import requests

from transit.exceptions import TransitException
from transit.modules.bart import urls

def _make_request(url):
    headers = {'accept-encoding' : 'gzip, deflate'}
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        raise TransitException(f'URL: "{url}" does not return 200')
    return r.json()

def service_advisory(bart_api_key):
    '''
    System wide service advisory

    bart_api_key : Use api key for request
    '''
    url = urls.service_advisory(bart_api_key)
    return _make_request(url)['root']

def train_count(bart_api_key):
    '''
    System wide train count

    bart_api_key : Use api key for request
    '''
    url = urls.train_count(bart_api_key)
    return _make_request(url)['root']

def elevator_status(bart_api_key):
    '''
    System wide elevator status

    bart_api_key : Use api key for request
    '''
    url = urls.elevator_status(bart_api_key)
    return _make_request(url)['root']

def station_list(bart_api_key):
    '''
    List of all service stations

    bart_api_key : Use api key for request
    '''
    url = urls.station_list(bart_api_key)
    return _make_request(url)['root']

def station_departures(bart_api_key, origin, platform=None, direction=None):
    '''
    Estimated departures for station

    bart_api_key :  Use api key for request
    origin       :  Short key for origin station, for all stations use 'ALL'
    platform     :  Limit results to a single platform
    direction    :  Limit results to a particular direction
    '''
    url = urls.station_departures(bart_api_key, origin, platform=platform, direction=direction)
    return _make_request(url)['root']
