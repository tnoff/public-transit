from transit.urls import nextbus
from transit.common import utils

class Stop(object):
    def __init__(self, stop_data, encoding):
        self.tag = stop_data.get('tag').encode(encoding)
        self.title = stop_data.get('title').encode(encoding)
        self.latitude = float(stop_data.get('lat').encode(encoding))
        self.longitude = float(stop_data.get('lon').encode(encoding))
        self.stop_id = int(stop_data.get('stopid').encode(encoding))
        try:
            self.short_title = stop_data.get('shorttitle').encode(encoding)
        except AttributeError:
            self.short_title = None

    def __repr__(self):
        return '%s - %s' % (self.tag, self.title)


class Point(object):
    def __init__(self, point_data, encoding):
        self.latitude = float(point_data.get('lat').encode(encoding))
        self.longitude = float(point_data.get('lon').encode(encoding))

    def __repr__(self):
        return '%s - %s' % (self.latitude, self.longitude)

class RoutePrediction(object):
    def __init__(self, route_data, encoding):
        self.route_tag = route_data.get('routetag').encode(encoding)
        self.agency_title = route_data.get('agencytitle').encode(encoding)
        self.route_title = route_data.get('routetitle').encode(encoding)
        self.stop_title = route_data.get('stoptitle').encode(encoding)
        self.directions = []
        self.messages = []

    def __repr__(self):
        return '%s - %s - %s' % \
            (self.agency_title, self.stop_title, self.route_tag)

class RouteDirectionPrediction(object):
    def __init__(self, direction_data, encoding):
        self.title = direction_data.get('title').encode(encoding)
        self.predictions = []

    def __repr__(self):
        return '%s' % self.title

class RouteStopPrediction(object):
    def __init__(self, stop_data, encoding):
        self.seconds = int(stop_data.get('seconds').encode(encoding))
        self.minutes = int(stop_data.get('minutes').encode(encoding))
        self.epochtime = int(stop_data.get('epochtime').encode(encoding))
        self.trip_tag = stop_data.get('triptag').encode(encoding)
        self.vehicle = stop_data.get('vehicle').encode(encoding)
        self.block = stop_data.get('block').encode(encoding)
        self.dir_tag = stop_data.get('dirtag').encode(encoding)
        self.is_departure = False
        if stop_data.get('isdeparture').encode(encoding) == 'true':
            self.is_departure = True
        self.affected_by_layover = False
        try:
            if stop_data.get('affectedbylayover').encode(encoding) == 'true':
                self.affected_by_layover = True
        except AttributeError:
            # data not present
            pass
    def __repr__(self):
        return '%s:%s - %s' % (self.minutes, self.seconds, self.vehicle)

def stop_prediction(agency_tag, stop_id, route_tag=None):
    '''Predict arrivals at stop, for only route tag if specified'''
    # Different url depending on route_tag
    url = nextbus.stop_prediction(agency_tag, stop_id, route_tag=route_tag)
    soup, encoding = utils.make_request(url)
    # Add all stop predictions for routes
    route_predictions = []
    for new_route in soup.find_all('predictions'):
        route_pred = RoutePrediction(new_route, encoding)
        # All directions in route
        for direction in new_route.find_all('direction'):
            # Find all predictions in direction
            new_dir = RouteDirectionPrediction(direction, encoding)
            for pred in direction.find_all('prediction'):
                new_dir.predictions.append(RouteStopPrediction(pred, encoding))
            route_pred.directions.append(new_dir)
        for message in new_route.find_all('message'):
            route_pred.messages.append(message.get('text').encode('utf-8'))
        route_predictions.append(route_pred)
    return route_predictions

def multiple_stop_prediction(agency_tag, stop_data):
    '''Stop Data in format {route_tag : [stoptag, stoptag, ..], ...}'''
    url = nextbus.multiple_stop_prediction(agency_tag, stop_data)
    soup, encoding = utils.make_request(url)
    route_predictions = []
    for new_route in soup.find_all('predictions'):
        route_pred = RoutePrediction(new_route, encoding)
        # All directions in route
        for direction in new_route.find_all('direction'):
            # Find all predictions in direction
            new_dir = RouteDirectionPrediction(direction, encoding)
            for pred in direction.find_all('prediction'):
                new_dir.predictions.append(RouteStopPrediction(pred, encoding))
            route_pred.directions.append(new_dir)
        for message in new_route.find_all('message'):
            route_pred.messages.append(message.get('text').encode('utf-8'))
        route_predictions.append(route_pred)
    return route_predictions
