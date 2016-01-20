from transit.common import utils as common_utils
from transit.modules.bart import urls, utils

def _route(route_data, encoding):
    data = {}
    args = ['name', 'abbr', 'number', 'color', 'routeid']
    for arg in args:
        value = common_utils.parse_data(route_data, arg)
        data[arg] = common_utils.clean_value(value, encoding)
    data['abbreviation'] = data.pop('abbr', None)
    # this is silly, it returns "ROUTE 1" instead of just int(1)
    route_id = data.pop('routeid')
    data['route_id'] = int(route_id.replace('ROUTE', ''))
    return data

def _route_info(route_data, encoding):
    data = _route(route_data, encoding)
    args = ['origin', 'destination', 'holidays', 'num_stns']
    for arg in args:
        value = common_utils.parse_data(route_data, arg)
        data[arg] = common_utils.clean_value(value, encoding)
    data['holidays'] = int(data.pop('holidays', 0)) == 1
    data['stations'] = []
    for station in route_data.find_all('station'):
        data['stations'].append(common_utils.clean_value(station.contents[0], encoding))
    return data

def route_list(schedule=None, date=None):
    url = urls.route_list(schedule=schedule, date=date)
    soup, encoding = utils.make_request(url)
    routes = []
    for route in soup.find_all('route'):
        route_data = _route(route, encoding)
        routes.append(route_data)
    return routes

def route_info(route_number, schedule=None, date=None):
    url = urls.route_info(route_number, schedule=schedule, date=date)
    soup, encoding = utils.make_request(url)
    return _route_info(soup.find('route'), encoding)
