from bs4 import BeautifulSoup
import requests

from transit import utils
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
    '''
    List all nextbus agencies
    '''
    url = urls.agency_list()
    soup, encoding = _make_request(url)
    return [agency.agency(ag, encoding) for ag in soup.find_all('agency')]

def route_list(agency_tag):
    '''
    Get list of agency routes
    agency_tag      :   agency tag
    '''
    utils.check_args(agency_tag, [basestring])
    url = urls.route_list(agency_tag)
    soup, encoding = _make_request(url)
    return_data = []
    for route_data in soup.find_all('route'):
        return_data.append(route.route(route_data, encoding))
    return return_data

def route_show(agency_tag, route_tag):
    '''
    Get information about route
    agency_tag      :   agency tag
    route_tag       :   route_tag
    '''
    utils.check_args(agency_tag, [basestring])
    utils.check_args(route_tag, [basestring])
    url = urls.route_show(agency_tag, route_tag)
    soup, encoding = _make_request(url)
    return route.route_info(soup.find('route'), encoding)

def route_messages(agency_tag, route_tags):
    '''
    Get alert messages for routes
    agency_tag      :   agency tag
    route_tags      :   list of route tags
    '''
    utils.check_args(agency_tag, [basestring])
    utils.check_args(route_tags, [basestring], is_list=True)
    url = urls.message_get(agency_tag, route_tags)
    soup, encoding = _make_request(url)
    return [route.route_message(r, encoding) for r in soup.find_all('route')]

def schedule_get(agency_tag, route_tag):
    '''
    Get schedule information for route
    agency_tag      :   agency tag
    route_tag       :   route tag
    '''
    utils.check_args(agency_tag, [basestring])
    utils.check_args(route_tag, [basestring])
    url = urls.schedule_get(agency_tag, route_tag)
    soup, encoding = _make_request(url)
    return [schedule.schedule_route(r, encoding) for r in soup.find_all('route')]

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
    utils.check_args(agency_tag, [basestring])
    url = urls.multiple_stop_prediction(agency_tag, prediction_data)
    soup, encoding = _make_request(url)
    return [stop.route_prediction(pred, encoding) for pred in soup.find_all('predictions')]

def stop_prediction(agency_tag, stop_id, route_tags=None):
    '''
    Get arrival predictions for stops
    agency_tag      :   agency tag
    stop_id         :   stop id
    route_tags      :   list of routes
    '''
    utils.check_args(agency_tag, [basestring])
    utils.check_args(stop_id, [basestring])
    utils.check_args(route_tags, [basestring], allow_none=True, is_list=True)
    url = urls.stop_prediction(agency_tag, stop_id, route_tags=route_tags)
    soup, encoding = _make_request(url)
    routes = []
    # if only a single route was entered into url, only single result with that
    # .. route will be returned. if multiple routes, use routes here to strip
    # .. the data
    for pred in soup.find_all('predictions'):
        try:
            routes.append(stop.route_prediction(pred, encoding, route_tags=route_tags))
        except SkipException:
            continue
    return routes

def vehicle_location(agency_tag, route_tag, epoch_time):
    '''
    Get vehicle location for route at time
    agency_tag      :   agency tag
    route_tag       :   route tag
    epoch_time      :   epoch time for locations
    '''
    utils.check_args(agency_tag, [basestring])
    utils.check_args(route_tag, [basestring])
    utils.check_args(epoch_time, [int])
    url = urls.vehicle_location(agency_tag, route_tag, epoch_time)
    soup, encoding = _make_request(url)
    return [vehicle.vehicle_location(veh, encoding) for veh in soup.find_all('vehicle')]
