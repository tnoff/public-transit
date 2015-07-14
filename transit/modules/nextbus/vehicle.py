from transit.urls import nextbus
from transit.common import utils

class VehicleLocation(object): #pylint: disable=too-many-instance-attributes
    def __init__(self, vehicle_data, encoding):
        self.vehicle_id = int(vehicle_data.get('id').encode(encoding))
        self.heading = vehicle_data.get('heading').encode(encoding)
        self.latitude = float(vehicle_data.get('lat').encode(encoding))
        self.longitude = float(vehicle_data.get('lon').encode(encoding))
        # Not present sometimes
        try:
            self.route_tag = vehicle_data.get('routetag').encode(encoding)
        except AttributeError:
            self.route_tag = None
        self.seconds_since_last_report = \
            int(vehicle_data.get('secssincereport').encode(encoding))
        self.speed_km_hr = float(vehicle_data.get('speedkmhr').encode(encoding))
        self.predictable = False
        if vehicle_data.get('predictable').encode(encoding) == "true":
            self.predictable = True

    def __repr__(self):
        return '%s:%s-%s' % (self.vehicle_id, self.latitude, self.longitude)

def vehicle_location(agency_tag, route_tag, epoch_time):
    url = nextbus.vehicle_location(agency_tag, route_tag, epoch_time)
    soup, encoding = utils.make_request(url)
    return [VehicleLocation(i, encoding) for i in soup.find_all('vehicle')]
