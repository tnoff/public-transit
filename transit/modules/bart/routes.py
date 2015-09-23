from transit.common import utils as common_utils
from transit.modules.bart import urls, utils

class RouteBase(object):
    def __init__(self, route_data, encoding):
        self.name = common_utils.parse_data(route_data, 'name', encoding)
        self.abbreviation = common_utils.parse_data(route_data, 'abbr', encoding)
        # this is silly, it returns "ROUTE 1" instead of just int(1)
        route_id = common_utils.parse_data(route_data, 'routeid', encoding)
        self.route_id = int(route_id.replace('ROUTE', ''))
        self.number = common_utils.parse_data(route_data, 'number', encoding)
        self.color = common_utils.parse_data(route_data, 'color', encoding)

    def __repr__(self):
        return '%s - %s' % (self.name, self.number)

class Route(RouteBase):
    def __init__(self, route_data, encoding):
        RouteBase.__init__(self, route_data, encoding)

    def route_info(self, schedule=None, date=None):
        return route_info(self.number, schedule=schedule, date=date)

class RouteInfo(RouteBase):
    def __init__(self, route_data, encoding):
        RouteBase.__init__(self, route_data, encoding)
        self.origin = common_utils.parse_data(route_data, 'origin', encoding)
        self.destination = common_utils.parse_data(route_data, 'destination',
                                                   encoding)
        # i assume this means "runs on holidays", but I have no clue
        holidays = common_utils.parse_data(route_data, 'holidays', encoding)
        self.holidays = (holidays == 1)
        self.number_stations = common_utils.parse_data(route_data, 'num_stns', encoding)
        self.stations = []
        for station in route_data.find_all('station'):
            self.stations.append(station.contents[0].encode(encoding))

def route_list(schedule=None, date=None):
    url = urls.route_list(schedule=schedule, date=date)
    soup, encoding = utils.make_request(url)
    return [Route(i, encoding) for i in soup.find_all('route')]

def route_info(route_number, schedule=None, date=None):
    url = urls.route_info(route_number, schedule=schedule, date=date)
    soup, encoding = utils.make_request(url)
    return RouteInfo(soup.find('route'), encoding)
