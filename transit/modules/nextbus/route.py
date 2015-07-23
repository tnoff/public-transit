from datetime import datetime

from transit.exceptions import TransitException
from transit.modules.nextbus import urls, utils
from transit.modules.nextbus import schedule, stop, vehicle

class RouteBase(object):
    def __init__(self, data, encoding, agency_tag=None):
        self.route_tag = data.get('tag').encode(encoding)
        self.agency_tag = agency_tag

    def __repr__(self):
        return '%s' % self.route_tag

class Route(RouteBase):
    def __init__(self, data, encoding, agency_tag=None):
        RouteBase.__init__(self, data, encoding, agency_tag=agency_tag)
        self.title = data.get('title').encode(encoding)

class RouteInfo(RouteBase): #pylint: disable=too-many-instance-attributes
    def __init__(self, data, encoding, agency_tag=None):
        RouteBase.__init__(self, data, encoding, agency_tag=agency_tag)
        self.title = data.get('title').encode(encoding)
        self.color = data.get('color').encode(encoding)
        self.opposite_color = data.get('oppositecolor').encode(encoding)
        self.latitude_min = float(data.get('latmin').encode(encoding))
        self.latitude_max = float(data.get('latmax').encode(encoding))
        self.longitdue_min = float(data.get('lonmin').encode(encoding))
        self.longitude_max = float(data.get('lonmax').encode(encoding))
        self.stops = []
        self.paths = []
        self.directions = []

        # Add all complete stop data
        # Directions will have stops with just "tags"
        # Ignore those for now
        for new_stop in data.find_all('stop'):
            if not new_stop.get('stopid'):
                continue
            self.stops.append(stop.Stop(new_stop, encoding))
        for direction in data.find_all('direction'):
            new_dir = RouteDirection(direction, encoding)
            # now add all stop tags
            for i in direction.find_all('stop'):
                new_dir.stop_tags.append(i.get('tag').encode(encoding))
            self.directions.append(new_dir)
        for path in data.find_all('path'):
            path_points = [stop.Point(i, encoding) \
                for i in path.find_all('point')]
            self.paths.append(path_points)

    def schedule_get(self):
        if not self.agency_tag:
            raise TransitException("Cannot get schedule w/o agency tag")
        return schedule.schedule_get(self.agency_tag, self.route_tag)

    def stop_prediction(self, stop_id):
        if not self.agency_tag:
            raise TransitException("Cannot get schedule w/o agency tag")
        return stop.stop_prediction(self.agency_tag, stop_id,
                                    route_tags=self.route_tag)

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
    def __init__(self, direction_data, encoding):
        self.tag = direction_data.get('tag').encode(encoding)
        self.name = direction_data.get('name').encode(encoding)
        self.title = direction_data.get('title').encode(encoding)
        self.use_for_ui = False
        if direction_data.get('useforui').encode(encoding) == 'true':
            self.use_for_ui = True
        self.stop_tags = []

    def __repr__(self):
        return '%s - %s' % (self.title, self.tag)

class Message(object): #pylint: disable=too-many-instance-attributes
    def __init__(self, data, encoding):
        self.message_id = int(data.get('id').encode(encoding))
        self.priority = data.get('priority').encode(encoding)
        try:
            self.start_boundary_time = float(data.get('startboundary').enocde(encoding))
        except AttributeError:
            self.start_boundary = None
        try:
            self.end_boundary_time = float(data.get('endboundary').encode(encoding))
        except AttributeError:
            self.end_boundary = None
        try:
            sb = datetime.strptime(data.get('startboundarystr'),
                                   "%a, %b %d %H:%M:%S %Z %Y")
            self.start_boundary = sb
        except (TypeError, AttributeError):
            self.start_boundary = None
        try:
            eb = datetime.strptime(data.get('endboundarystr'),
                                   "%a, %b %d %H:%M:%S %Z %Y")
            self.end_boundary = eb
        except (TypeError, AttributeError):
            self.end_boundary = None
        self.send_to_buses = False
        try:
            if data.get('senttobuses').encode(encoding) == 'true':
                self.send_to_buses = True
        except AttributeError:
            pass
        self.text = [i.contents[0].encode(encoding) \
            for i in data.find_all('text')]

    def __repr__(self):
        return '%s - %s' % (self.message_id, self.text)

class RouteMessage(RouteBase):
    def __init__(self, data, encoding, agency_tag=None):
        RouteBase.__init__(self, data, encoding, agency_tag=agency_tag)
        self.messages = [Message(i, encoding) for i in data.find_all("message")]

def route_list(agency_tag):
    url = urls.route_list(agency_tag)
    soup, encoding = utils.make_request(url)

    # Build route list
    return [Route(i, encoding, agency_tag=agency_tag) \
        for i in soup.find_all('route')]

def route_get(agency_tag, route_tag):
    url = urls.route_show(agency_tag, route_tag)
    soup, encoding = utils.make_request(url)
    # Get route data
    return RouteInfo(soup.find('route'), encoding, agency_tag=agency_tag)

def message_get(agency_tag, route_tags):
    url = urls.message_get(agency_tag, route_tags)
    soup, encoding = utils.make_request(url)
    return [RouteMessage(i, encoding) for i in soup.find_all('route')]
