# Agency interface
from transit.agency import Agency
from transit.route import Route, RoutePrediction, RouteStopPrediction, Point
from transit.route import ScheduleRoute, ScheduleStop, Stop
from transit.vehicle import VehicleLocation
from transit import urls
from transit import utils

def __next_real_sibling(item):
    item = item.next_sibling
    while True:
        ok = True
        if item == '\n':
            ok = False
            item = item.next_sibling
        elif item == ' ':
            ok = False
            item = item.next_sibling
        elif item == '':
            ok = False
            item = item.next_sibling
        if ok:
            break
    return item

def agency_list():
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

def agency_search(key, value):
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

def route_list(agency_tag):
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

def route_get(agency_tag, route_tag):
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
        stop = __next_real_sibling(stop)
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

def schedule_get(agency_tag, route_tag):
    url = urls.schedule['show'] % (agency_tag, route_tag)
    soup = utils.make_request(url)

    route_list = []
    for route in soup.find_all('route'):
        sr = ScheduleRoute(route.get('tag'),
                           route.get('title'),
                           route.get('scheduleclass'),
                           route.get('serviceclass'),
                           route.get('direction'))
        for block in route.find_all('tr'):
            for stop in block.find_all('stop'):
                sr.schedule_stops.append(ScheduleStop(stop.get('tag'),
                                                      stop.get('epochtime'),
                                                      stop.string,
                                                      block.get('blockid')))

        route_list.append(sr)
    return route_list

def vehicle_location(agency_tag, route_tag, epoch_time):
    url = urls.vehicle['location'] % (agency_tag, route_tag, epoch_time)
    soup = utils.make_request(url)

    vehicle_list = []
    for vehicle in soup.find_all('vehicle'):
        vehicle_list.append(VehicleLocation(vehicle.get('id'),
                                            vehicle.get('heading'),
                                            vehicle.get('lat'),
                                            vehicle.get('lon'),
                                            vehicle.get('routetag'),
                                            vehicle.get('secssincereport'),
                                            vehicle.get('speedkmhr'),
                                            vehicle.get('predictable'),))

    return vehicle_list
