from transit.common import utils
from transit.urls import bart

class RouteBase(object):
    def __init__(self, route_data, encoding):
        self.name = utils.pretty_strip(route_data.find('name'), encoding)
        self.abbreviation = utils.pretty_strip(route_data.find('abbr'),
                                               encoding)
        # this is silly, it returns "ROUTE 1" instead of just int(1)
        route_id_string = utils.pretty_strip(route_data.find('routeid'),
                                             encoding)
        self.route_id = int(route_id_string.replace('ROUTE', ''))
        self.number = int(utils.pretty_strip(route_data.find('number'),
                                             encoding))
        self.color = utils.pretty_strip(route_data.find('color'), encoding)

    def __repr__(self):
        return '%s - %s' % (self.name, self.number)

class Route(RouteBase):
    def __init__(self, route_data, encoding):
        RouteBase.__init__(self, route_data, encoding)

    def route_show(self, schedule=None, date=None):
        return route_show(self.number, schedule=schedule, date=date)

class RouteInfo(RouteBase):
    def __init__(self, route_data, encoding):
        RouteBase.__init__(self, route_data, encoding)
        self.origin = utils.pretty_strip(route_data.find('origin'), encoding)
        self.destination = utils.pretty_strip(route_data.find('destination'),
                                              encoding)
        # i assume this means "runs on holidays", but I have no clue
        self.holidays = int(utils.pretty_strip(route_data.find('holidays'),
                                               encoding)) == 1
        self.number_stations = int(utils.pretty_strip(route_data.find('num_stns'),
                                                      encoding))
        self.stations = []
        for station in route_data.find_all('station'):
            self.stations.append(utils.pretty_strip(station, encoding))

def route_list(schedule=None, date=None):
    url = bart.route_list(schedule=schedule, date=date)
    soup, encoding = utils.make_request(url)
    return [Route(i, encoding) for i in soup.find_all('route')]

def route_show(route_number, schedule=None, date=None):
    url = bart.route_show(route_number, schedule=schedule, date=date)
    soup, encoding = utils.make_request(url)
    return RouteInfo(soup.find('route'), encoding)
