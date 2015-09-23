from transit.common import utils as common_utils
from transit.modules.nextbus import urls, utils
from transit.exceptions import TransitException

class Stop(object):
    def __init__(self, data, encoding):
        self.tag = common_utils.parse_data(data, 'tag', encoding)
        self.title = common_utils.parse_data(data, 'title', encoding)
        self.latitude = common_utils.parse_data(data, 'lat', encoding)
        self.longitude = common_utils.parse_data(data, 'lon', encoding)
        self.stop_id = common_utils.parse_data(data, 'stopid', encoding)
        self.short_title = common_utils.parse_data(data, 'shortttile', encoding)

    def __repr__(self):
        return '%s - %s' % (self.tag, self.title)


class Point(object):
    def __init__(self, point_data, encoding):
        self.latitude = common_utils.parse_data(point_data, 'lat', encoding)
        self.longitude = common_utils.parse_data(point_data, 'lon', encoding)

    def __repr__(self):
        return '%s lat- %s lon' % (self.latitude, self.longitude)


class RoutePrediction(object):
    def __init__(self, route_data, encoding, route_tags=None):
        self.route_tag = common_utils.parse_data(route_data, 'routetag', encoding)
        # Raise exception here for multiple stop excludes
        # .. that way you dont get a bunch of data you dont care about
        if route_tags:
            if str(self.route_tag).lower() not in route_tags:
                raise TransitException("Tag not allowed:%s" % self.route_tag)
        self.agency_title = common_utils.parse_data(route_data, 'agencytitle',
                                                    encoding)
        self.route_title = common_utils.parse_data(route_data, 'routetitle',
                                                   encoding)
        self.stop_title = common_utils.parse_data(route_data, 'stoptitle',
                                                  encoding)
        self.directions = []
        self.messages = []

        # All directions in route
        self.directions = [RouteDirectionPrediction(i, encoding) \
            for i in route_data.find_all('direction')]
        for message in route_data.find_all('message'):
            self.messages.append(message.get('text').encode('utf-8'))

    def __repr__(self):
        return '%s - %s - %s' % \
            (self.agency_title, self.stop_title, self.route_tag)

class RouteDirectionPrediction(object):
    def __init__(self, direction_data, encoding):
        self.title = common_utils.parse_data(direction_data, 'title', encoding)
        self.predictions = []
        # Find all predictions in direction
        for pred in direction_data.find_all('prediction'):
            self.predictions.append(RouteStopPrediction(pred, encoding))

    def __repr__(self):
        return '%s' % self.title

class RouteStopPrediction(object): #pylint: disable=too-many-instance-attributes
    def __init__(self, data, encoding):
        self.seconds = common_utils.parse_data(data, 'seconds', encoding)
        self.minutes = common_utils.parse_data(data, 'minutes', encoding)
        self.epoch_time = common_utils.parse_data(data, 'epochtime', encoding)
        self.trip_tag = common_utils.parse_data(data, 'triptag', encoding)
        self.vehicle = common_utils.parse_data(data, 'vehicle', encoding)
        self.block = common_utils.parse_data(data, 'block', encoding)
        self.dir_tag = common_utils.parse_data(data, 'dirtag', encoding)
        self.is_departure = common_utils.parse_data(data, 'isdeparture', encoding)
        self.affected_by_layover = common_utils.parse_data(data,
                                                           'affectedbylayover',
                                                           encoding)
        # this is not listed if false sometimes
        if not self.affected_by_layover:
            self.affected_by_layover = False

    def __repr__(self):
        time = common_utils.pretty_time(self.minutes, self.seconds)
        return '%s - %s' % (time, self.vehicle)

def stop_prediction(agency_tag, stop_id, route_tags=None):
    # Treat this two different ways for route tags
    # .. if route tag is only a single route, it will make the call directly
    # .. and you dont have to do anything fancy
    # .. if there is a list of route tags, get all route tags and strip
    # .. during the call
    tags = None
    if isinstance(route_tags, list):
        if len(route_tags) == 1:
            route_tags = route_tags[0]
        else:
            tags = [i.lower() for i in route_tags]

    url = urls.stop_prediction(agency_tag, stop_id, route_tags=route_tags)
    soup, encoding = utils.make_request(url)
    routes = []
    for i in soup.find_all('predictions'):
        try:
            routes.append(RoutePrediction(i, encoding, route_tags=tags))
        except TransitException:
            continue
    return routes

def multiple_stop_prediction(agency_tag, data):
    url = urls.multiple_stop_prediction(agency_tag, data)
    soup, encoding = utils.make_request(url)
    return [RoutePrediction(i, encoding) \
                            for i in soup.find_all('predictions')]
