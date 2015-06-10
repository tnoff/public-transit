class Route(object):
    def __init__(self, tag, title, short_title=None,
                 color=None, opposite_color=None, latitude_min=None,
                 latitude_max=None, longitude_min=None, longitude_max=None):
        # Present Everywhere
        self.tag = tag.encode('utf-8')
        self.title = title.encode('utf-8')
        # Present only in route show or route list
        try:
            self.short_title = short_title.encode('utf-8')
        except AttributeError:
            self.short_title = None
        try:
            self.color = color.encode('utf-8')
        except AttributeError:
            self.color = None
        try:
            self.opposite_color = opposite_color.encode('utf-8')
        except AttributeError:
            self.opposite_color = None
        try:
            self.latitude_min = float(latitude_min.encode('utf-8'))
        except AttributeError:
            self.latitude_min = None
        try:
            self.latitude_max = float(latitude_max.encode('utf-8'))
        except AttributeError:
            self.lititude_max = None
        try:
            self.longitdue_min = float(longitude_min.encode('utf-8'))
        except AttributeError:
            self.longitdue_min = None
        try:
            self.longitude_max = float(longitude_max.encode('utf-8'))
        except AttributeError:
            self.longitude_max = None
        self.stops = []
        self.paths = []

    def __repr__(self):
        return '%s - %s' % (self.tag, self.title)


class Stop(object):
    def __init__(self, tag, title, short_title, latitude, longitude, stop_id):
        self.tag = tag.encode('utf-8')
        self.title = title.encode('utf-8')
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.stop_id = int(stop_id)
        self.directions = []
        try:
            self.short_title = short_title.encode('utf-8')
        except AttributeError:
            self.short_title = None

    def __repr__(self):
        return '%s - %s' % (self.tag, self.title)


class Point(object):
    def __init__(self, latitude, longitude):
        self.latitude = float(latitude.encode('utf-8'))
        self.longitude = float(longitude.encode('utf-8'))

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
