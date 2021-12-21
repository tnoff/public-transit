from collections import OrderedDict
import requests
import xmltodict

from transit.exceptions import TransitException
from transit.modules.nextbus import urls

def post_process(_path, key, value):
    if isinstance(value, OrderedDict):
        value = dict(value)
    if key[0] == '@':
        key = key[1:]
    return key, value

def _make_request(url):
    headers = {'accept-encoding' : 'gzip, deflate'}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise TransitException(f'Non-200 status code returned, {r.status_code} - {r.text}')

    return dict(xmltodict.parse(r.text, postprocessor=post_process))

def agency_list():
    '''
    List all nextbus agencies
    '''
    url = urls.agency_list()
    return _make_request(url)['body']

def route_list(agency_tag):
    '''
    Get list of agency routes
    agency_tag      :   agency tag
    '''
    url = urls.route_list(agency_tag)
    return _make_request(url)['body']

def route_show(agency_tag, route_tag):
    '''
    Get information about route
    agency_tag      :   agency tag
    route_tag       :   route_tag
    '''
    url = urls.route_show(agency_tag, route_tag)
    return _make_request(url)['body']

def route_messages(agency_tag, route_tags):
    '''
    Get alert messages for routes
    agency_tag      :   agency tag
    route_tags      :   list of route tags
    '''
    url = urls.message_get(agency_tag, route_tags)
    return _make_request(url)['body']

def stop_prediction(agency_tag, stop_id, route_tags=None):
    '''
    Get arrival predictions for stops
    agency_tag      :   agency tag
    stop_id         :   stop id
    route_tags      :   list of routes
    '''
    url = urls.stop_prediction(agency_tag, stop_id, route_tags=route_tags)
    return  _make_request(url)['body']

def stop_multiple_predictions(agency_tag, prediction_data):
    '''
    Get predictions for multiple stops
    agency_tag      :   agency tag
    prediction_data :   {
        "stop_tag1" : [route1, route2],
        "stop_tag2" : [route3],
        # must provide at least one route per stop tag
    }
    '''
    url = urls.multiple_stop_prediction(agency_tag, prediction_data)
    print(f'Url {url}')
    return _make_request(url)['body']
