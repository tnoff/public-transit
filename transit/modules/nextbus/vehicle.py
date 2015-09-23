from transit.common import utils as common_utils
from transit.modules.nextbus import urls, utils

class VehicleLocation(object): #pylint: disable=too-many-instance-attributes
    def __init__(self, vehicle_data, encoding):
        self.vehicle_id = common_utils.parse_data(vehicle_data, 'id', encoding)
        self.heading = common_utils.parse_data(vehicle_data, 'heading', encoding)
        self.latitude = common_utils.parse_data(vehicle_data, 'lat', encoding)
        self.longitude = common_utils.parse_data(vehicle_data, 'lon', encoding)

        self.route_tag = common_utils.parse_data(vehicle_data, 'routetag', encoding)
        self.seconds_since_last_report = \
            common_utils.parse_data(vehicle_data, 'secssincereport', encoding)
        self.speed_km_hr = common_utils.parse_data(vehicle_data, 'speedkmhr', encoding)
        self.predictable = common_utils.parse_data(vehicle_data, 'predictable', encoding)

    def __repr__(self):
        return '%s:%s-%s' % (self.vehicle_id, self.latitude, self.longitude)

def vehicle_location(agency_tag, route_tag, epoch_time):
    url = urls.vehicle_location(agency_tag, route_tag, epoch_time)
    soup, encoding = utils.make_request(url)
    return [VehicleLocation(i, encoding) for i in soup.find_all('vehicle')]
