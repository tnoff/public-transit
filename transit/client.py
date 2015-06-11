# Agency interface
from transit import agency
from transit import route
from transit import stop
from transit import schedule
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
    return schedule.schedule_get(agency_tag, route_tag)

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
