from transit.common import utils as common_utils
from transit.modules.nextbus import urls, utils
from transit.exceptions import TransitException

def _stop(stop_data, encoding):
    data = {}
    stop_tag = common_utils.parse_data(stop_data, 'tag')
    data['stop_tag'] = common_utils.clean_value(stop_tag, encoding)
    title = common_utils.parse_data(stop_data, 'title')
    data['title'] = common_utils.clean_value(title, encoding)
    latitude = common_utils.parse_data(stop_data, 'lat')
    data['latitude'] = common_utils.clean_value(latitude, encoding)
    longitude = common_utils.parse_data(stop_data, 'lon')
    data['longitude'] = common_utils.clean_value(longitude, encoding)
    stop_id = common_utils.parse_data(stop_data, 'stopid')
    data['stop_id'] = common_utils.clean_value(stop_id, encoding)
    short_title = common_utils.parse_data(stop_data, 'shortttile')
    data['short_title'] = common_utils.clean_value(short_title, encoding)
    return data

def _point(point_data, encoding):
    data = {}
    latitude = common_utils.parse_data(point_data, 'lat')
    data['latitude'] = common_utils.clean_value(latitude, encoding)
    longitude = common_utils.parse_data(point_data, 'lon')
    data['longitude'] = common_utils.clean_value(longitude, encoding)
    return data

def _route_prediction(route_data, encoding, route_tags=None):
    data = {}
    route_tag = common_utils.parse_data(route_data, 'routetag')
    data['route_tag'] = common_utils.clean_value(route_tag, encoding)

    # Raise exception here for multiple stop excludes
    # .. that way you dont get a bunch of data you dont care about
    if route_tags and route_tag.lower() not in route_tags:
        raise TransitException("Tag not allowed:%s" % data['route_tag'])

    agency_title = common_utils.parse_data(route_data, 'agencytitle')
    data['agency_title'] = common_utils.clean_value(agency_title, encoding)
    route_title = common_utils.parse_data(route_data, 'routetitle')
    data['route_title'] = common_utils.clean_value(route_title, encoding)
    stop_title = common_utils.parse_data(route_data, 'stoptitle')
    data['stop_title'] = common_utils.clean_value(stop_title, encoding)

    data['directions'] = []
    data['messages'] = []

    # All directions in route
    for direction in route_data.find_all('direction'):
        data['directions'].append(_route_direction_prediction(direction, encoding))
    for message in route_data.find_all('message'):
        text = message.get('text')
        data['messages'].append(common_utils.clean_value(text, encoding))
    return data

def _route_direction_prediction(direction_data, encoding):
    data = {}
    title = common_utils.parse_data(direction_data, 'title')
    data['title'] = common_utils.clean_value(title, encoding)
    data['predictions'] = []
    # Find all predictions in direction
    for pred in direction_data.find_all('prediction'):
        data['predictions'].append(_route_stop_prediction(pred, encoding))
    return data

def _route_stop_prediction(pred_data, encoding):
    data = {}
    args = ['seconds', 'minutes', 'block', 'vehicle']
    for arg in args:
        value = common_utils.parse_data(pred_data, arg)
        data[arg] = common_utils.clean_value(value, encoding)

    epoch_time = common_utils.parse_data(pred_data, 'epochtime')
    data['epoch_time'] = common_utils.clean_value(epoch_time, encoding)
    trip_tag = common_utils.parse_data(pred_data, 'triptag')
    data['trip_tag'] = common_utils.clean_value(trip_tag, encoding)
    dir_tag = common_utils.parse_data(pred_data, 'dirtag')
    data['dir_tag'] = common_utils.clean_value(dir_tag, encoding)
    is_departure = common_utils.parse_data(pred_data, 'isdeparture')
    data['is_departure'] = common_utils.clean_value(is_departure, encoding)
    layover = common_utils.parse_data(pred_data, 'affectedbylayover')
    data['affected_by_layover'] = common_utils.clean_value(layover, encoding)
    if not data['affected_by_layover']:
        data['affected_by_layover'] = False
    return data

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
    soup, encoding = utils.make_request(url)
    routes = []
    # if only a single route was entered into url, only single result with that
    # .. route will be returned. if multiple routes, use routes here to strip
    # .. the data
    if route_tags and isinstance(route_tags, list):
        route_tags = [item.lower() for item in route_tags]
    for pred in soup.find_all('predictions'):
        try:
            routes.append(_route_prediction(pred, encoding, route_tags=route_tags))
        except TransitException:
            continue
    return routes

def stop_multiple_predictions(agency_tag, data):
    '''Get predictions for multiple stops
       agency_tag: agency tag
       stop_data:{route_tag : [stoptag, stoptag, ..], ...}
    '''
    assert isinstance(agency_tag, basestring), 'agency tag must be string type'
    # TODO assert stopdata with jsonschema
    url = urls.multiple_stop_prediction(agency_tag, data)
    soup, encoding = utils.make_request(url)
    return [_route_prediction(pred, encoding) for pred in soup.find_all('predictions')]
