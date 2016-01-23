from transit.common import utils as common_utils
from transit.modules.nextbus import urls, utils
from transit.exceptions import TransitException

def _stop(stop_data, encoding):
    args = ['tag', 'title', 'lat', 'lon', 'stopid', 'shortttile']
    data = common_utils.parse_page(stop_data, args, encoding)
    data['stop_tag'] = data.pop('tag', None)
    data['latitude'] = data.pop('lat', None)
    data['longitude'] = data.pop('lon', None)
    data['stop_id'] = data.pop('stopid', None)
    data['short_title'] = data.pop('shortttile', None)
    return data

def _point(point_data, encoding):
    args = ['lat', 'lon']
    data = common_utils.parse_page(point_data, args, encoding)
    data['latitude'] = data.pop('lat', None)
    data['longitude'] = data.pop('lon', None)
    return data

def _route_prediction(route_data, encoding, route_tags=None):
    data = common_utils.parse_page(route_data, ['routetag'], encoding)
    data['route_tag'] = data.pop('routetag', None)
    # Raise exception here for multiple stop excludes
    # .. that way you dont get a bunch of data you dont care about
    if route_tags and data['route_tag'].lower() not in route_tags:
        raise TransitException("Tag not allowed:%s" % data['route_tag'])

    args = ['agencytitle', 'routetitle', 'stoptitle']
    additional_data = common_utils.parse_page(route_data, args, encoding)
    data['agency_title'] = additional_data.pop('agencytitle', None)
    data['route_title'] = additional_data.pop('routetitle', None)
    data['stop_title'] = additional_data.pop('stoptitle', None)
    data['directions'] = []
    data['messages'] = []

    # All directions in route
    for direction in route_data.find_all('direction'):
        data['directions'].append(_route_direction_prediction(direction, encoding))
    for message in route_data.find_all('message'):
        data['messages'].append(common_utils.parse_page(message, ['text'], encoding)['text'])
    return data

def _route_direction_prediction(direction_data, encoding):
    data = common_utils.parse_page(direction_data, ['title'], encoding)
    data['predictions'] = []
    # Find all predictions in direction
    for pred in direction_data.find_all('prediction'):
        data['predictions'].append(_route_stop_prediction(pred, encoding))
    return data

def _route_stop_prediction(pred_data, encoding):
    args = ['seconds', 'minutes', 'block', 'vehicle', 'epochtime', 'triptag',
            'dirtag', 'isdeparture', 'affectedbylayover']
    data = common_utils.parse_page(pred_data, args, encoding)
    data['epoch_time'] = data.pop('epochtime', None)
    data['trip_tag'] = data.pop('triptag', None)
    data['dir_tag'] = data.pop('dirtag', None)
    data['is_departure'] = data.pop('isdeparture', None)
    data['affected_by_layover'] = data.pop('affectedbylayover', None)
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
