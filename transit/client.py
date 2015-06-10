# Agency interface
from transit import agency
from transit import route
from transit.vehicle import VehicleLocation
from transit import urls
from transit import utils

def agency_list():
    return agency.list_all()

def route_list(agency_tag):
    return route.route_list(agency_tag)

def route_get(agency_tag, route_tag):
    return route.route_get(agency_tag, route_tag)

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
        route_pred = route.RoutePrediction(new_route.get('routetag'),
                                           new_route.get('agencytitle'),
                                           new_route.get('routetitle'),
                                           new_route.get('stoptitle'))
        # All directions in route
        for direction in new_route.find_all('direction'):
            # Find all predictions in direction
            for pred in direction.find_all('prediction'):
                route_pred.predictions.append(route.RouteStopPrediction(\
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
        for message in new_route.find_all('message'):
            route_pred.messages.append(message.get('text').encode('utf-8'))
        route_predictions.append(route_pred)
    return route_predictions

def schedule_get(agency_tag, route_tag):
    url = urls.schedule['show'] % (agency_tag, route_tag)
    soup = utils.make_request(url)

    new_route_list = []
    for new_route in soup.find_all('route'):
        sr = route.ScheduleRoute(new_route.get('tag'),
                                 new_route.get('title'),
                                 new_route.get('scheduleclass'),
                                 new_route.get('serviceclass'),
                                 new_route.get('direction'))
        for block in new_route.find_all('tr'):
            for stop in block.find_all('stop'):
                sr.schedule_stops.append(route.ScheduleStop(stop.get('tag'),
                                                            stop.get('epochtime'),
                                                            stop.string,
                                                            block.get('blockid')))

        new_route_list.append(sr)
    return new_route_list

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
