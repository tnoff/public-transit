from transit.common import urls, utils

class VehicleLocation(object):
    def __init__(self, vehicle_data):
        self.vehicle_id = int(vehicle_data.get('id').encode('utf-8'))
        self.heading = vehicle_data.get('heading').encode('utf-8')
        self.latitude = float(vehicle_data.get('lat').encode('utf-8'))
        self.longitude = float(vehicle_data.get('lon').encode('utf-8'))
        self.route_tag = vehicle_data.get('routetag').encode('utf-8')
        self.seconds_since_last_report = \
            int(vehicle_data.get('secssincereport').encode('utf-8'))
        self.speed_km_hr = float(vehicle_data.get('speedkmhr').encode('utf-8'))
        self.predictable = False
        if vehicle_data.get('predictable').encode('utf-8') == "true":
            self.predictable = True

    def __repr__(self):
        return '%s:%s-%s' % (self.vehicle_id, self.latitude, self.longitude)

def vehicle_location(agency_tag, route_tag, epoch_time):
    url = urls.vehicle['location'] % (agency_tag, route_tag, epoch_time)
    soup = utils.make_request(url)

    vehicle_list = [VehicleLocation(i) for i in soup.find_all('vehicle')]
    return vehicle_list
