import requests
import xmltodict

from transit.exceptions import TransitException
from transit.modules.nextbus import urls

def post_process(_path: str, key: str, value: object) -> tuple[str, object]:
    if isinstance(value, dict):
        value = dict(value)
    if key[0] == '@':
        key = key[1:]
    return key, value

def _make_request(url: str) -> dict:
    headers = {'accept-encoding' : 'gzip, deflate'}
    r = requests.get(url, timeout=120, headers=headers)
    if r.status_code != 200:
        raise TransitException(f'Non-200 status code returned, {r.status_code} - {r.text}')

    return dict(xmltodict.parse(r.text, postprocessor=post_process))

def agency_list() -> dict:
    '''
    List all nextbus agencies
    '''
    url = urls.agency_list()
    return _make_request(url)['body']

def route_list(agency_tag: str) -> dict:
    '''
    Get list of agency routes
    agency_tag      :   agency tag
    '''
    url = urls.route_list(agency_tag)
    return _make_request(url)['body']

def route_show(agency_tag: str, route_tag: str) -> dict:
    '''
    Get information about route
    agency_tag      :   agency tag
    route_tag       :   route_tag
    '''
    url = urls.route_show(agency_tag, route_tag)
    return _make_request(url)['body']

def route_messages(agency_tag: str, route_tags: list[str]) -> dict:
    '''
    Get alert messages for routes
    agency_tag      :   agency tag
    route_tags      :   list of route tags
    '''
    url = urls.message_get(agency_tag, route_tags)
    return _make_request(url)['body']

def stop_prediction(agency_tag: str, stop_id: str | int, route_tags: list[str] | str | None = None) -> dict:
    '''
    Get arrival predictions for stops
    agency_tag      :   agency tag
    stop_id         :   stop id
    route_tags      :   list of routes
    '''
    url = urls.stop_prediction(agency_tag, stop_id, route_tags=route_tags)
    return  _make_request(url)['body']

def stop_multiple_predictions(agency_tag: str, prediction_data: dict[str, list[str]]) -> dict:
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
    return _make_request(url)['body']
