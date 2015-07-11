from transit.common import utils
from transit.urls import bart

class ScheduleRoute(object):
    def __init__(self, route_data, encoding):
        self.name = utils.pretty_strip(route_data.find('name'), encoding)
        self.abbreviation = utils.pretty_strip(route_data.find('abbr'),
                                               encoding)
        # this is silly, it returns "ROUTE 1" instead of just int(1)
        route_id_string = utils.pretty_strip(route_data.find('routeid'), encoding)
        self.route_id = int(route_id_string.replace('ROUTE', ''))
        self.number = int(utils.pretty_strip(route_data.find('number'),
                                             encoding))
        self.color = utils.pretty_strip(route_data.find('color'), encoding)

        # rest are only in route info calls
        try:
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
        except AttributeError:
            self.origin = None
            self.destination = None
            self.holidays = None
            self.number_stations = None

    def __repr__(self):
        return '%s - %s' % (self.route_id, self.name)

class Schedule(object):
    def __init__(self, schedule_data, encoding):
        self.schedule_number = int(utils.pretty_strip(schedule_data.find('sched_num'),
                                                      encoding))
        self.routes = []
        for route in schedule_data.find_all('route'):
            self.routes.append(ScheduleRoute(route, encoding))

    def __repr__(self):
        return '%s' % self.schedule_number

def current_routes(schedule=None, date=None):
    url = bart.current_routes(schedule=schedule, date=date)
    soup, encoding = utils.make_request(url)
    return Schedule(soup, encoding)

def route_info(route_number, schedule=None, date=None):
    url = bart.route_info(route_number, schedule=schedule, date=date)
    soup, encoding = utils.make_request(url)
    return ScheduleRoute(soup.find('route'), encoding)
