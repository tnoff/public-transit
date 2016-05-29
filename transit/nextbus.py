from bs4 import BeautifulSoup
import requests

from transit.exceptions import SkipException, TransitException
from transit.modules.nextbus import urls
from transit.modules.nextbus import agency, route, stop, schedule, vehicle

def _make_request(url, markup="html.parser"):
    headers = {'accept-encoding' : 'gzip, deflate'}
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        raise TransitException("Non-200 status code returned")

    soup = BeautifulSoup(r.text, markup)
    # Get encoding from top of XML data
    contents = soup.contents
    if str(contents[0]) == '\n':
        del contents[0]
    encoding = str(soup.contents[0].split('encoding')[1])
    encoding = encoding.lstrip('="').rstrip('"')
    # check for errors
    error = soup.find('error')
    # nextbus just gives error message in error
    if error:
        error_string = error.string
        error_string = error_string.lstrip('\n').rstrip('\n')
        error_string = error_string.lstrip(' ').rstrip(' ')
        raise TransitException(error_string)
    return soup, encoding

def agency_list():
    '''List all nextbus agencies'''
    url = urls.agency_list()
    soup, encoding = _make_request(url)
    return [agency.agency(ag, encoding) for ag in soup.find_all('agency')]

def route_list(agency_tag):
    '''Get list of agency routes
       agency_tag: agency tag
    '''
    assert isinstance(agency_tag, basestring), 'agency tag must be string type'
    url = urls.route_list(agency_tag)
    soup, encoding = _make_request(url)
    return_data = []
    for route_data in soup.find_all('route'):
        return_data.append(route.route(route_data, encoding))
    return return_data

def route_get(agency_tag, route_tag):
    '''Get information about route
       agency_tag: agency tag
       route_tag : route_tag
    '''
    assert isinstance(agency_tag, basestring), 'agency tag must be string type'
    assert isinstance(route_tag, basestring), 'route tag must be string type'
    url = urls.route_show(agency_tag, route_tag)
    soup, encoding = _make_request(url)
    return route.route_info(soup.find('route'), encoding)

def route_messages(agency_tag, route_tags):
    '''Get alert messages for routes
       agency_tag : agency tag
       route_tags : either single route tag, or list of tags
    '''
    assert isinstance(agency_tag, basestring), 'agency tag must be string type'
    assert isinstance(route_tags, basestring) or isinstance(route_tags, list),\
        'route tag must be string type or list of string types'
    url = urls.message_get(agency_tag, route_tags)
    soup, encoding = _make_request(url)
    return [route.route_message(r, encoding) for r in soup.find_all('route')]

def schedule_get(agency_tag, route_tag):
    '''Get schedule information for route
       agency_tag : agency tag
       route_tag : route tag
    '''
    assert isinstance(agency_tag, basestring), 'agency tag must be string type'
    assert isinstance(route_tag, basestring), 'route tag must be string type'
    url = urls.schedule_get(agency_tag, route_tag)
    soup, encoding = _make_request(url)
    return [schedule.schedule_route(r, encoding) for r in soup.find_all('route')]

def stop_multiple_predictions(agency_tag, prediction_data):
    '''Get predictions for multiple stops
       agency_tag: agency tag
       prediction_data : {
            "stop_tag1" : [route1, route2],
            "stop_tag2" : [route3],
            # must provide at least one route per stop tag
       }
    '''
    assert isinstance(agency_tag, basestring), 'agency tag must be string type'
    assert isinstance(prediction_data, dict), 'prediction data must be dict type'
    for key in prediction_data.keys():
        assert isinstance(key, basestring), 'prediction data key must be string type'
        lowered = key.lower()
        if key != lowered:
            prediction_data[lowered] = prediction_data.pop(key)
        assert isinstance(prediction_data[lowered], list),\
            'prediction data value must be list type'
        assert len(prediction_data[lowered]) > 0,\
            'prediction data value list must be populated'
        for item in prediction_data[lowered]:
            assert isinstance(item, basestring),\
                'prediction data value item must be string type'

    url = urls.multiple_stop_prediction(agency_tag, prediction_data)
    soup, encoding = _make_request(url)
    return [stop.route_prediction(pred, encoding) for pred in soup.find_all('predictions')]

def stop_prediction(agency_tag, stop_id, route_tags=None):
    '''Get arrival predictions for stops
       agency_tag: agency tag
       stop_id: stop id
       route_tags: list of routes or single route to limit search
    '''
    assert isinstance(agency_tag, basestring), 'agency tag must be string type'
    assert isinstance(stop_id, basestring), 'stop id must be string type'
    assert route_tags is None or isinstance(route_tags, basestring)\
        or isinstance(route_tags, list), \
            'route tags must be string, list or null type'
    url = urls.stop_prediction(agency_tag, stop_id, route_tags=route_tags)
    soup, encoding = _make_request(url)
    routes = []
    # if only a single route was entered into url, only single result with that
    # .. route will be returned. if multiple routes, use routes here to strip
    # .. the data
    if route_tags and isinstance(route_tags, list):
        route_tags = [item.lower() for item in route_tags]
    for pred in soup.find_all('predictions'):
        try:
            routes.append(stop.route_prediction(pred, encoding, route_tags=route_tags))
        except SkipException:
            continue
    return routes

def vehicle_location(agency_tag, route_tag, epoch_time):
    '''Get vehicle location for route at time
       agency_tag: agency tag
       route_tag: route tag
       epoch_time: epoch time for locations
    '''
    assert isinstance(agency_tag, basestring), 'agency tag must be string type'
    assert isinstance(route_tag, basestring), 'route tag must be string type'
    assert isinstance(epoch_time, int), 'epoch time must be int type'
    url = urls.vehicle_location(agency_tag, route_tag, epoch_time)
    soup, encoding = _make_request(url)
    return [vehicle.vehicle_location(veh, encoding) for veh in soup.find_all('vehicle')]
