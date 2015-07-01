from datetime import datetime

from transit.exceptions import TransitException
from transit.urls import nextbus
from transit.common import utils

from transit.modules.nextbus import schedule, stop, vehicle

class Route(object):
    def __init__(self, route_data, agency_tag=None):
        # Present Everywhere
        self.route_tag = route_data.get('tag').encode('utf-8')
        # Can be entered in for sanity
        self.agency_tag = agency_tag
        # Present only in route show or route list
        try:
            self.title = route_data.get('title').encode('utf-8')
        except AttributeError:
            self.title = None
        try:
            self.short_title = route_data.get('shorttitle').encode('utf-8')
        except AttributeError:
            self.short_title = None
        try:
            self.color = route_data.get('color').encode('utf-8')
        except AttributeError:
            self.color = None
        try:
            self.opposite_color = route_data.get('oppositecolor').encode('utf-8')
        except AttributeError:
            self.opposite_color = None
        try:
            self.latitude_min = float(route_data.get('latmin').encode('utf-8'))
        except AttributeError:
            self.latitude_min = None
        try:
            self.latitude_max = float(route_data.get('latmax').encode('utf-8'))
        except AttributeError:
            self.lititude_max = None
        try:
            self.longitdue_min = float(route_data.get('lonmin').encode('utf-8'))
        except AttributeError:
            self.longitdue_min = None
        try:
            self.longitude_max = float(route_data.get('lonmax').encode('utf-8'))
        except AttributeError:
            self.longitude_max = None
        self.stops = []
        self.paths = []
        self.directions = []
        self.messages = []

    def schedule_get(self):
        if not self.agency_tag:
            raise TransitException("Cannot get schedule w/o agency tag")
        return schedule.schedule_get(self.agency_tag, self.route_tag)

    def stop_prediction(self, stop_id):
        if not self.agency_tag:
            raise TransitException("Cannot get schedule w/o agency tag")
        return stop.stop_prediction(self.agency_tag, stop_id,
                                    route_tag=self.route_tag)

    def vehicle_location(self, epoch_time):
        if not self.agency_tag:
            raise TransitException("Cannot get schedule w/o agency tag")
        return vehicle.vehicle_location(self.agency_tag, self.route_tag,
                                        epoch_time)

    def message_get(self):
        if not self.agency_tag:
            raise TransitException("Cannot get schedule w/o agency tag")
        return message_get(self.agency_tag, self.route_tag)

    def __repr__(self):
        return '%s - %s' % (self.route_tag, self.title)

class RouteDirection(object):
    def __init__(self, direction_data):
        self.tag = direction_data.get('tag').encode('utf-8')
        self.name = direction_data.get('name').encode('utf-8')
        self.title = direction_data.get('title').encode('utf-8')
        self.use_for_ui = False
        if direction_data.get('useforui').encode('utf-8') == 'true':
            self.use_for_ui = True
        self.stop_tags = []

    def __repr__(self):
        return '%s - %s' % (self.title, self.tag)

class RouteMessage(object):
    def __init__(self, message_data):
        self.message_id = int(message_data.get('id').encode('utf-8'))
        self.priority = message_data.get('priority').encode('utf-8')
        try:
            self.start_boundary_time = float(message_data.get('startboundary').enocde('utf-8'))
        except AttributeError:
            self.start_boundary = None
        try:
            self.end_boundary_time = float(message_data.get('endboundary').encode('utf-8'))
        except AttributeError:
            self.end_boundary = None
        try:
            sb = datetime.strptime(message_data.get('startboundarystr'),
                                   "%a, %b %d %H:%M:%S %Z %Y")
            self.start_boundary = sb
        except (TypeError, AttributeError):
            self.start_boundary = None
        try:
            eb = datetime.strptime(message_data.get('endboundarystr'),
                                   "%a, %b %d %H:%M:%S %Z %Y")
            self.end_boundary = eb
        except (TypeError, AttributeError):
            self.end_boundary = None
        self.send_to_buses = False
        try:
            if message_data.get('senttobuses').encode('utf-8') == 'true':
                self.send_to_buses = True
        except AttributeError:
            pass
        self.text = [i.contents[0].encode('utf-8') for i in message_data.find_all('text')]

    def __repr__(self):
        return '%s - %s' % (self.message_id, self.text)

def route_list(agency_tag):
    '''List routes for agency'''
    url = nextbus.route_list(agency_tag)
    soup = utils.make_request(url)

    # Build route list
    return [Route(i, agency_tag=agency_tag) for i in soup.find_all('route')]

def route_get(agency_tag, route_tag):
    '''Get route information'''
    url = nextbus.route_show(agency_tag, route_tag)
    soup = utils.make_request(url)
    # Get route data
    route_data = soup.find('route')
    new_route = Route(route_data, agency_tag=agency_tag)
    # Add all complete stop data
    # Directions will have stops with just "tags"
    # Ignore those for now
    for new_stop in soup.find_all('stop'):
        if not new_stop.get('stopid'):
            continue
        new_route.stops.append(stop.Stop(new_stop))
    for direction in soup.find_all('direction'):
        new_dir = RouteDirection(direction)
        # now add all stop tags
        for i in direction.find_all('stop'):
            new_dir.stop_tags.append(i.get('tag').encode('utf-8'))
        new_route.directions.append(new_dir)
    for path in soup.find_all('path'):
        path_points = [stop.Point(i) for i in path.find_all('point')]
        new_route.paths.append(path_points)
    return new_route

def message_get(agency_tag, route_tags):
    '''route_tags should be list of route_tags'''
    url = nextbus.message_get(agency_tag, route_tags)
    soup = utils.make_request(url)
    routes = []
    for new_route in soup.find_all('route'):
        r = Route(new_route)
        for message in new_route.find_all("message"):
            r.messages.append(RouteMessage(message))
        routes.append(r)
    return routes
