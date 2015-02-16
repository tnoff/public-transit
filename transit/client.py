# Agency interface
from transit import urls
from transit import utils

class Agency(object):
    def __init__(self, tag, title, region):
        self.tag = tag.encode('utf-8')
        self.title = title.encode('utf-8')
        self.region = region.encode('utf-8')

    def __repr__(self):
        return '%s - %s - %s' % (self.title, self.region, self.tag)


class Route(object):
    def __init__(self, tag, title, short_title,
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


class Client(object):
    def __init__(self):
        pass

    def agency_list(self):
        '''Get list of agencies'''
        url = urls.agency['list']
        soup = utils.make_request(url)

        # Build agency list
        agency_list = []
        for agency in soup.find_all('agency'):
            agency_list.append(Agency(agency.get('tag'),
                                      agency.get('title'),
                                      agency.get('regiontitle')))
        return agency_list

    def agency_search(self, key, value):
        '''Search for agency with value in key'''
        url = urls.agency['list']
        soup = utils.make_request(url)

        # Search for agency, return list of matching
        agency_list = []
        nice_value = value.lower().replace(' ', '')
        nice_key = key.lower().replace(' ', '')
        for agency in soup.find_all('agency'):
            for key in agency.attrs.keys():
                if nice_key in key.encode('utf-8'):
                    search_value = agency.get(key).encode('utf-8').lower().replace(' ', '')
                    if nice_value in search_value:
                        agency_list.append(Agency(agency.get('tag'),
                                                  agency.get('title'),
                                                  agency.get('regiontitle')))
                        break
        return agency_list

    def route_list(self, agency_tag):
        '''List routes for agency'''
        url = urls.route['list'] % agency_tag
        soup = utils.make_request(url)

        # Build route list
        route_list = []
        for route in soup.find_all('route'):
            route_list.append(Route(route.get('tag'),
                                    title=route.get('title'),
                                    short_title=route.get('shorttitle')))
        return route_list

    def __next_real_sibling(self, item):
        item = item.next_sibling
        while True:
            if item == '\n':
                item = item.next_sibling
                continue
            if item == ' ':
                item = item.next_sibling
                continue
            break
        return item

    def route_get(self, agency_tag, route_tag):
        '''Get route information'''
        url = urls.route['show'] % (agency_tag, route_tag)
        soup = utils.make_request(url)
        # Get route data
        r = soup.find('route')

        route = Route(r.get('tag'), title=r.get('title'),
                      short_title=r.get('shorttile'),
                      color=r.get('color'), opposite_color=r.get('opposite_color'),
                      latitude_min=r.get('latmin'), latitude_max=r.get('latmax'),
                      longitude_min=r.get('lonmin'), longitude_max=r.get('longmax'))
        # Get all stop data
        # Find all stops until first direction
        # Otherwise you list all stops per direction
        stop = r.find('stop')
        # Stop dict : {stop_tag, index in route stop list}
        stop_dict = dict()
        stop_count = 0
        while True:
            route.stops.append(Stop(stop.get('tag'), stop.get('title'),
                                    stop.get('shorttitle'), stop.get('lat'),
                                    stop.get('lon'), stop.get('stopid')))
            stop_dict[stop.get('tag').encode('utf-8')] = stop_count
            stop_count += 1
            stop = self.__next_real_sibling(stop)
            if stop.name != 'stop':
                break
        # Get all direction data
        for direction in r.find_all('direction'):
            # Get all stop tags in direction
            # Find stop tag, then add direction when can
            for stop in direction.find_all('stop'):
                stop_index = stop_dict[stop.get('tag').encode('utf-8')]
                route.stops[stop_index].directions.append(\
                    direction.get('title').encode('utf-8'))
        # Add paths to route
        for path in r.find_all('path'):
            path_points = []
            for point in path.find_all('point'):
                path_points.append(Point(point.get('lat'), point.get('lon')))
            route.paths.append(path_points)
        return route

    def stop_prediction(self, agency_tag, stop_id, route_tag=None):
        '''Predict arrivals at stop, for only route tag if specified'''
        # Different url depending on route_tag
        if route_tag:
            url = urls.predictions['route'] % (agency_tag, stop_id, route_tag)
        else:
            url = urls.predictions['stop'] % (agency_tag, stop_id)
        soup = utils.make_request(url)
        # Add all stop predictions for routes
        route_predictions = []
        for route in soup.find_all('predictions'):
            route_pred = RoutePrediction(route.get('routetag'),
                                         route.get('agencytitle'),
                                         route.get('routetitle'),
                                         route.get('stoptitle'))
            # All directions in route
            for direction in route.find_all('direction'):
                # Find all predictions in direction
                for pred in direction.find_all('prediction'):
                    route_pred.predictions.append(RouteStopPrediction(\
                                    direction.get('title'),
                                    pred.get('seconds'),
                                    pred.get('minutes'),
                                    pred.get('epochtime'),
                                    pred.get('triptag'),
                                    pred.get('vehicle'),
                                    pred.get('block'),
                                    pred.get('dirtag'),
                                    pred.get('isdeparture'),
                                    pred.get('affectedbylayover'),))
            for message in route.find_all('message'):
                route_pred.messages.append(message.get('text').encode('utf-8'))
            route_predictions.append(route_pred)
        return route_predictions
