from transit import utils
from transit.exceptions import SkipException

def stop(stop_data, encoding):
    args = ['tag', 'title', 'lat', 'lon', 'stopid', 'shortttile']
    data = utils.parse_page(stop_data, args, encoding)
    data['stop_tag'] = data.pop('tag', None)
    data['latitude'] = data.pop('lat', None)
    data['longitude'] = data.pop('lon', None)
    data['stop_id'] = data.pop('stopid', None)
    data['short_title'] = data.pop('shortttile', None)
    return data

def point(point_data, encoding):
    args = ['lat', 'lon']
    data = utils.parse_page(point_data, args, encoding)
    data['latitude'] = data.pop('lat', None)
    data['longitude'] = data.pop('lon', None)
    return data

def route_prediction(route_data, encoding, route_tags=None):
    data = utils.parse_page(route_data, ['routetag'], encoding)
    data['route_tag'] = data.pop('routetag', None)
    # Raise exception here for multiple stop excludes
    # .. that way you dont get a bunch of data you dont care about
    if route_tags and data['route_tag'] not in route_tags:
        raise SkipException("Tag not allowed:%s" % data['route_tag'])

    args = ['agencytitle', 'routetitle', 'stoptitle']
    additional_data = utils.parse_page(route_data, args, encoding)
    data['agency_title'] = additional_data.pop('agencytitle', None)
    data['route_title'] = additional_data.pop('routetitle', None)
    data['stop_title'] = additional_data.pop('stoptitle', None)
    data['directions'] = []
    data['messages'] = []

    # All directions in route
    for direction in route_data.find_all('direction'):
        data['directions'].append(route_direction_prediction(direction, encoding))
    for message in route_data.find_all('message'):
        data['messages'].append(utils.parse_page(message, ['text'], encoding)['text'])
    return data

def route_direction_prediction(direction_data, encoding):
    data = utils.parse_page(direction_data, ['title'], encoding)
    data['predictions'] = []
    # Find all predictions in direction
    for pred in direction_data.find_all('prediction'):
        data['predictions'].append(route_stop_prediction(pred, encoding))
    return data

def route_stop_prediction(pred_data, encoding):
    args = ['seconds', 'minutes', 'block', 'vehicle', 'epochtime', 'triptag',
            'dirtag', 'isdeparture', 'affectedbylayover']
    data = utils.parse_page(pred_data, args, encoding)
    data['epoch_time'] = data.pop('epochtime', None)
    data['trip_tag'] = data.pop('triptag', None)
    data['dir_tag'] = data.pop('dirtag', None)
    data['is_departure'] = data.pop('isdeparture', None)
    data['affected_by_layover'] = data.pop('affectedbylayover', None)
    if not data['affected_by_layover']:
        data['affected_by_layover'] = False
    return data
