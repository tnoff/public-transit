from transit.exceptions import TransitException

from transit.common import utils as common_utils
from transit.modules.nextbus import urls, utils
from transit.modules.nextbus import schedule, stop, vehicle

def _route_base(route_data, agency_tag=None):
    data = {}
    data['route_tag'] = common_utils.parse_data(route_data, 'tag')
    data['agency_tag'] = agency_tag
    return data

def _route(route_data, agency_tag=None):
    data = _route_base(route_data, agency_tag=agency_tag)
    data['title'] = common_utils.parse_data(route_data, 'title')
    return data

def _route_info(route_data, agency_tag=None):
    data = _route_base(route_data, agency_tag=agency_tag)
    args = ['title', 'color', 'oppositecolor', 'latmin', 'latmax', 'lonmin', 'lonmax']
    for arg in args:
        value = common_utils.parse_data(route_data, arg)
        data[arg] = value
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
        data['stops'].append(stop._stop(new_stop))

    for direction in route_data.find_all('direction'):
        new_dir = _route_direction(direction)
        # now add all stop tags for each direction
        for i in direction.find_all('stop'):
            new_dir['stop_tags'].append(i.get('tag'))
        data['directions'].append(new_dir)

    for path in route_data.find_all('path'):
        path_points = [stop._point(i) \
            for i in path.find_all('point')]
        data['paths'].append(path_points)
    return data

def _route_direction(direction_data):
    data = {}
    data['tag'] = common_utils.parse_data(direction_data, 'tag')
    data['name'] = common_utils.parse_data(direction_data, 'name')
    data['title'] = common_utils.parse_data(direction_data, 'title')
    data['use_for_ui'] = common_utils.parse_data(direction_data, 'useforui')
    data['stop_tags'] = []
    return data

def _message(message_data):
    data = {}
    data['message_id'] = common_utils.parse_data(message_data, 'id')
    data['priority'] = common_utils.parse_data(message_data, 'priority')
    data['start_boundary_epoch'] = common_utils.parse_data(message_data, 'startboundary')
    data['end_boundary_epoch'] = common_utils.parse_data(message_data, 'endboundary')
    data['start_boundary'] = common_utils.parse_data(message_data, 'startboundarystr')
    data['end_boundary'] = common_utils.parse_data(message_data, 'endboundarystr')
    data['send_to_buses'] = common_utils.parse_data(message_data, 'senttobuses')
    data['text'] = [i.contents[0] for i in message_data.find_all('text')]
    return data

def _route_message(route_data, agency_tag=None):
    data = _route_base(route_data, agency_tag=agency_tag)
    data['messages'] = [_message(i) for i in route_data.find_all('message')]
    return data

def route_list(agency_tag):
    url = urls.route_list(agency_tag)
    soup, encoding = utils.make_request(url)

    # Build route list
    return [_route(i, agency_tag=agency_tag) for i in soup.find_all('route')]

def route_get(agency_tag, route_tag):
    url = urls.route_show(agency_tag, route_tag)
    soup, encoding = utils.make_request(url)
    # Get route data
    return _route_info(soup.find('route'), agency_tag=agency_tag)

def message_get(agency_tag, route_tags):
    url = urls.message_get(agency_tag, route_tags)
    soup, encoding = utils.make_request(url)
    return [_route_message(i) for i in soup.find_all('route')]
