from transit import urls
from transit import utils

def route_list(agency_tag):
    '''List routes for agency'''
    url = urls.route['list'] % agency_tag
    soup = utils.make_request(url)

    # Build route list
    return [Route(i) for i in soup.find_all('route')]

def route_get(agency_tag, route_tag):
    '''Get route information'''
    url = urls.route['show'] % (agency_tag, route_tag)
    soup = utils.make_request(url)
    # Get route data
    route_data = soup.find('route')
    new_route = Route(route_data)
    # Add all complete stop data
    # Directions will have stops with just "tags"
    # Ignore those for now
    for stop in soup.find_all('stop'):
        if not stop.get('stopid'):
            continue
        new_route.stops.append(Stop(stop))
    for direction in soup.find_all('direction'):
        new_dir = RouteDirection(direction)
        # now add all stop tags
        for i in direction.find_all('stop'):
            new_dir.stop_tags.append(i.encode('utf-8'))
        new_route.directions.append(new_dir)
    for path in soup.find_all('path'):
        path_points = [Point(i) for i in path.find_all('point')]
        new_route.paths.append(path_points)
    return new_route

class Route(object):
    def __init__(self, route_data):
        # Present Everywhere
        self.tag = route_data.get('tag').encode('utf-8')
        self.title = route_data.get('title').encode('utf-8')
        # Present only in route show or route list
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

    def __repr__(self):
        return '%s - %s' % (self.tag, self.title)

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

class Stop(object):
    def __init__(self, stop_data):
        self.tag = stop_data.get('tag').encode('utf-8')
        self.title = stop_data.get('title').encode('utf-8')
        self.latitude = float(stop_data.get('lat').encode('utf-8'))
        self.longitude = float(stop_data.get('lon').encode('utf-8'))
        self.stop_id = int(stop_data.get('stopid').encode('utf-8'))
        try:
            self.short_title = stop_data.get('shorttitle').encode('utf-8')
        except AttributeError:
            self.short_title = None

    def __repr__(self):
        return '%s - %s' % (self.tag, self.title)


class Point(object):
    def __init__(self, point_data):
        self.latitude = float(point_data.get('lat').encode('utf-8'))
        self.longitude = float(point_data.get('lon').encode('utf-8'))

    def __repr__(self):
        return '%s - %s' % (self.latitude, self.longitude)


class RoutePrediction(object):
    def __init__(self, route_tag, agency_title, route_title, stop_title):
        self.route_tag = route_tag.encode('utf-8')
        self.agency_title = agency_title.encode('utf-8')
        self.route_title = route_title.encode('utf-8')
        self.stop_title = stop_title.encode('utf-8')
        self.predictions = []
        self.messages = []

    def __repr__(self):
        return '%s - %s - %s' % (self.agency_title, self.stop_title, self.route_tag)


class RouteStopPrediction(object):
    def __init__(self, direction, seconds, minutes, epochtime, trip_tag, vehicle,
                 block, dir_tag, is_departure, affected_by_layover):
        self.direction = direction.encode('utf-8')
        self.seconds = int(seconds)
        self.minutes = int(minutes)
        self.epochtime = int(epochtime)
        self.trip_tag = trip_tag.encode('utf-8')
        self.vehicle = vehicle.encode('utf-8')
        self.block = block.encode('utf-8')
        self.dir_tag = dir_tag.encode('utf-8')
        self.is_departure = False
        if is_departure.encode('utf-8') == 'true':
            self.is_departure = True
        self.affected_by_layover = False
        try:
            if affected_by_layover.encode('utf-8') == 'true':
                self.affected_by_layover = True
        except AttributeError:
            pass

    def __repr__(self):
        return '%s:%s - %s' % (self.minutes, self.seconds, self.vehicle)


class ScheduleRoute(object):
    def __init__(self, tag, title, schedule_class, service_class, direction):
        self.tag = tag.encode('utf-8')
        self.title = title.encode('utf-8')
        self.schedule_class = schedule_class.encode('utf-8')
        self.service_class = service_class.encode('utf-8')
        self.direction = direction.encode('utf-8')
        self.schedule_stops = []

    def __repr__(self):
        return '%s - %s - %s' % (self.tag, self.direction, self.service_class)


class ScheduleStop(object):
    def __init__(self, stop_tag, epoch_time, time, block_id):
        self.stop_tag = stop_tag.encode('utf-8')
        self.epoch_time = epoch_time.encode('utf-8')
        self.time = time.encode('utf-8')
        self.block_id = block_id.encode('utf-8')

    def __repr__(self):
        return '%s - %s' % (self.stop_tag, self.time)
