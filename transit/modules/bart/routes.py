from transit.common import utils as common_utils
from transit.modules.bart import urls, utils

def _route(route_data):
    data = {}
    args = ['name', 'abbr', 'number', 'color']
    for arg in args:
        value = common_utils.parse_data(route_data, arg)
        data[arg] = value
    data['abbreviation'] = data.pop('abbr', None)
    # this is silly, it returns "ROUTE 1" instead of just int(1)
    route_id = common_utils.parse_data(route_data, 'routeid')
    data['route_id'] = int(route_id.replace('ROUTE', ''))
    return data

def _route_info(route_data):
    data = _route(route_data)
    args = ['origin', 'destination', 'holidays', 'num_stns']
    for arg in args:
        value = common_utils.parse_data(route_data, arg)
        data[arg] = value
    data['holidays'] = int(data.pop('holidays', 0)) == 1
    data['stations'] = []
    for station in route_data.find_all('station'):
        data['stations'].append(station.contents[0])
    return data

def route_list(schedule=None, date=None):
    url = urls.route_list(schedule=schedule, date=date)
    soup, encoding = utils.make_request(url)
    return [_route(i) for i in soup.find_all('route')]

def route_info(route_number, schedule=None, date=None):
    url = urls.route_info(route_number, schedule=schedule, date=date)
    soup, encoding = utils.make_request(url)
    return _route_info(soup.find('route'))
