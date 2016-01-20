from transit.common import utils as common_utils
from transit.modules.nextbus import urls, utils
from transit.modules.nextbus import stop

def _route_base(route_data, encoding, agency_tag=None):
    data = {}
    data['agency_tag'] = agency_tag
    route_tag = common_utils.parse_data(route_data, 'tag')
    data['route_tag'] = common_utils.clean_value(route_tag, encoding)
    return data

def _route(route_data, encoding, agency_tag=None):
    data = _route_base(route_data, encoding, agency_tag=agency_tag)
    title = common_utils.parse_data(route_data, 'title')
    data['title'] = common_utils.clean_value(title, encoding)
    return data

def _route_info(route_data, encoding, agency_tag=None):
    data = _route_base(route_data, encoding, agency_tag=agency_tag)
    args = ['title', 'color', 'oppositecolor', 'latmin', 'latmax', 'lonmin', 'lonmax']
    for arg in args:
        value = common_utils.parse_data(route_data, arg)
        data[arg] = common_utils.clean_value(value, encoding)
    data['opposite_color'] = data.pop('oppositecolor', None)
    data['latitude_min'] = data.pop('latmin', None)
    data['latitude_max'] = data.pop('latmax', None)
    data['longitude_min'] = data.pop('lonmin', None)
    data['longitude_max'] = data.pop('lonmax', None)

    data['stops'] = []
    data['paths'] = []
    data['directions'] = []

    # Add all complete stop data
    # Directions will have stops with just "tags"
    # Ignore those for now
    for new_stop in route_data.find_all('stop'):
        if not new_stop.get('stopid'):
            continue
        data['stops'].append(stop._stop(new_stop, encoding))

    for direction in route_data.find_all('direction'):
        new_dir = _route_direction(direction, encoding)
        # now add all stop tags for each direction
        for i in direction.find_all('stop'):
            new_dir['stop_tags'].append(i.get('tag'))
        data['directions'].append(new_dir)

    for path in route_data.find_all('path'):
        path_points = []
        for point in path.find_all('point'):
            path_points.append(stop._point(point, encoding))
        data['paths'].append(path_points)
    return data

def _route_direction(direction_data, encoding):
    data = {}
    args = ['tag', 'name', 'title', 'useforui']
    for arg in args:
        value = common_utils.parse_data(direction_data, arg)
        data[arg] = common_utils.clean_value(value, encoding)
    data['use_for_ui'] = data.pop('useforui', None)
    data['stop_tags'] = []
    return data

def _message(message_data, encoding):
    data = {}
    message_id = common_utils.parse_data(message_data, 'id')
    data['message_id'] = common_utils.clean_value(message_id, encoding)
    priority = common_utils.parse_data(message_data, 'priority')
    data['priority'] = common_utils.clean_value(priority, encoding)
    start_boundary = common_utils.parse_data(message_data, 'startboundary')
    data['start_boundary_epoch'] = common_utils.clean_value(start_boundary, encoding)
    end_boundary = common_utils.parse_data(message_data, 'endboundary')
    data['end_boundary_epoch'] = common_utils.clean_value(end_boundary, encoding)
    start = common_utils.parse_data(message_data, 'startboundarystr')
    data['start_boundary'] = common_utils.clean_value(start, encoding)
    end = common_utils.parse_data(message_data, 'endboundarystr')
    data['end_boundary'] = common_utils.clean_value(end, encoding)
    bus = common_utils.parse_data(message_data, 'senttobuses')
    data['send_to_buses'] = common_utils.clean_value(bus, encoding)
    data['text'] = []
    for text in message_data.find_all('text'):
        data['text'].append(common_utils.clean_value(text.contents[0], encoding))
    return data

def _route_message(route_data, encoding, agency_tag=None):
    data = _route_base(route_data, encoding, agency_tag=agency_tag)
    data['messages'] = [_message(mes, encoding) for mes in route_data.find_all('message')]
    return data

def route_list(agency_tag):
    url = urls.route_list(agency_tag)
    soup, encoding = utils.make_request(url)
    return_data = []
    for route in soup.find_all('route'):
        return_data.append(_route(route, encoding, agency_tag=agency_tag))
    return return_data

def route_get(agency_tag, route_tag):
    url = urls.route_show(agency_tag, route_tag)
    soup, encoding = utils.make_request(url)
    return _route_info(soup.find('route'), encoding, agency_tag=agency_tag)

def message_get(agency_tag, route_tags):
    url = urls.message_get(agency_tag, route_tags)
    soup, encoding = utils.make_request(url)
    return [_route_message(route, encoding) for route in soup.find_all('route')]
