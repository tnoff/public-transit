from transit.common import urls, utils

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
    def __init__(self, route_data):
        self.route_tag = route_data.get('routetag').encode('utf-8')
        self.agency_title = route_data.get('agencytitle').encode('utf-8')
        self.route_title = route_data.get('routetitle').encode('utf-8')
        self.stop_title = route_data.get('stoptitle').encode('utf-8')
        self.directions = []
        self.messages = []

    def __repr__(self):
        return '%s - %s - %s' % (self.agency_title, self.stop_title, self.route_tag)

class RouteDirectionPrediction(object):
    def __init__(self, direction_data):
        self.title = direction_data.get('title').encode('utf-8')
        self.predictions = []

    def __repr__(self):
        return '%s' % self.title

class RouteStopPrediction(object):
    def __init__(self, stop_data):
        self.seconds = int(stop_data.get('seconds'))
        self.minutes = int(stop_data.get('minutes'))
        self.epochtime = int(stop_data.get('epochtime'))
        self.trip_tag = stop_data.get('triptag').encode('utf-8')
        self.vehicle = stop_data.get('vehicle').encode('utf-8')
        self.block = stop_data.get('block').encode('utf-8')
        self.dir_tag = stop_data.get('dirtag').encode('utf-8')
        self.is_departure = False
        if stop_data.get('isdeparture').encode('utf-8') == 'true':
            self.is_departure = True
        self.affected_by_layover = False
        try:
            if stop_data.get('affectedbylayover').encode('utf-8') == 'true':
                self.affected_by_layover = True
        except AttributeError:
            # data not present
            pass
    def __repr__(self):
        return '%s:%s - %s' % (self.minutes, self.seconds, self.vehicle)

def stop_prediction(agency_tag, stop_id, route_tag=None):
    '''Predict arrivals at stop, for only route tag if specified'''
    # Different url depending on route_tag
    if route_tag:
        url = urls.predictions['route'] % (agency_tag, stop_id, route_tag)
    else:
        url = urls.predictions['stop'] % (agency_tag, stop_id)
    soup = utils.make_request(url)
    # Add all stop predictions for routes
    route_predictions = []
    for new_route in soup.find_all('predictions'):
        route_pred = RoutePrediction(new_route)
        # All directions in route
        for direction in new_route.find_all('direction'):
            # Find all predictions in direction
            new_dir = RouteDirectionPrediction(direction)
            for pred in direction.find_all('prediction'):
                new_dir.predictions.append(RouteStopPrediction(pred))
            route_pred.directions.append(new_dir)
        for message in new_route.find_all('message'):
            route_pred.messages.append(message.get('text').encode('utf-8'))
        route_predictions.append(route_pred)
    return route_predictions

def multiple_stop_prediction(agency_tag, stop_data):
    '''Stop Data in format {route_tag : [stoptag, stoptag, ..], ...}'''
    url = urls.predictions['multi']['url'] % agency_tag
    # Start creating url suffixs
    route_tag, stop_list = stop_data.popitem()
    for stop_tag in stop_list:
        url += urls.predictions['multi']['suffix'] % (route_tag, stop_tag)
    soup = utils.make_request(url)
    route_predictions = []
    for new_route in soup.find_all('predictions'):
        route_pred = RoutePrediction(new_route)
        # All directions in route
        for direction in new_route.find_all('direction'):
            # Find all predictions in direction
            new_dir = RouteDirectionPrediction(direction)
            for pred in direction.find_all('prediction'):
                new_dir.predictions.append(RouteStopPrediction(pred))
        for message in new_route.find_all('message'):
            route_pred.messages.append(message.get('text').encode('utf-8'))
        route_predictions.append(route_pred)
    return route_predictions
