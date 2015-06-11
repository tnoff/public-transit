# Agency interface
from transit import agency
from transit import route
from transit import stop
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
    return stop.stop_prediction(agency_tag, stop_id, route_tag=route_tag)

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
