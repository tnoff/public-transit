from transit.common import utils as common_utils
from transit.modules.nextbus import urls, utils
from transit.exceptions import TransitException

def _stop(stop_data):
    data = {}
    data['stop_tag'] = common_utils.parse_data(stop_data, 'tag')
    data['title'] = common_utils.parse_data(stop_data, 'title')
    data['latitude'] = common_utils.parse_data(stop_data, 'lat')
    data['longitude'] = common_utils.parse_data(stop_data, 'lon')
    data['stop_id'] = common_utils.parse_data(stop_data, 'stopid')
    data['short_title'] = common_utils.parse_data(stop_data, 'shortttile')
    return data

def _point(point_data):
    data = {}
    data['latitude'] = common_utils.parse_data(point_data, 'lat')
    data['longitude'] = common_utils.parse_data(point_data, 'lon')
    return data

def _route_prediction(route_data, route_tags=None):
    data = {}
    data['route_tag'] = common_utils.parse_data(route_data, 'routetag')
    # Raise exception here for multiple stop excludes
    # .. that way you dont get a bunch of data you dont care about
    if route_tags:
        if str(data['route_tag']).lower() not in route_tags:
            raise TransitException("Tag not allowed:%s" % data['route_tag'])
    data['agency_title'] = common_utils.parse_data(route_data, 'agencytitle')
    data['route_title'] = common_utils.parse_data(route_data, 'routetitle')
    data['stop_title'] = common_utils.parse_data(route_data, 'stoptitle')
    data['directions'] = []
    data['messages'] = []

    # All directions in route
    data['directions'] = [_route_direction_prediction(i) for i in route_data.find_all('direction')]
    for message in route_data.find_all('message'):
        data['messages'].append(message.get('text'))
    return data

def _route_direction_prediction(direction_data):
    data = {}
    data['title'] = common_utils.parse_data(direction_data, 'title')
    data['predictions'] = []
    # Find all predictions in direction
    for pred in direction_data.find_all('prediction'):
        data['predictions'].append(_route_stop_prediction(pred))
    return data

def _route_stop_prediction(pred_data):
    data = {}
    data['seconds'] = common_utils.parse_data(pred_data, 'seconds')
    data['minutes'] = common_utils.parse_data(pred_data, 'minutes')
    data['epoch_time'] = common_utils.parse_data(pred_data, 'epochtime')
    data['trip_tag'] = common_utils.parse_data(pred_data, 'triptag')
    data['vehicle'] = common_utils.parse_data(pred_data, 'vehicle')
    data['block'] = common_utils.parse_data(pred_data, 'block')
    data['dir_tag'] = common_utils.parse_data(pred_data, 'dirtag')
    data['is_departure'] = common_utils.parse_data(pred_data, 'isdeparture')
    data['affected_by_layover'] = common_utils.parse_data(pred_data, 'affectedbylayover')
    if not data['affected_by_layover']:
        data['affected_by_layover'] = False
    return data

def stop_prediction(agency_tag, stop_id, route_tags=None):
    # Treat this two different ways for route tags
    # .. if route tag is only a single route, it will make the call directly
    # .. and you dont have to do anything fancy
    # .. if there is a list of route tags, get all route tags and strip
    # .. during the call
    tags = None
    if isinstance(route_tags, list):
        if len(route_tags) == 1:
            route_tags = route_tags[0]
        else:
            tags = [i.lower() for i in route_tags]

    url = urls.stop_prediction(agency_tag, stop_id, route_tags=route_tags)
    soup, encoding = utils.make_request(url)
    routes = []
    for i in soup.find_all('predictions'):
        try:
            routes.append(_route_prediction(i, route_tags=tags))
        except TransitException:
            continue
    return routes

def multiple_stop_prediction(agency_tag, data):
    url = urls.multiple_stop_prediction(agency_tag, data)
    soup, encoding = utils.make_request(url)
    return [_route_prediction(i) for i in soup.find_all('predictions')]
