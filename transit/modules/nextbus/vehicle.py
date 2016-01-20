from transit.common import utils as common_utils
from transit.modules.nextbus import urls, utils

def _vehicle_location(vehicle_data, encoding):
    data = {}
    args = ['id', 'heading', 'lat', 'lon', 'routetag', 'secssincereport', 'speedkmhr',
            'predictable']
    for arg in args:
        value = common_utils.parse_data(vehicle_data, arg)
        data[arg] = common_utils.clean_value(value, encoding)
    data['vehicle_id'] = data.pop('id', None)
    data['latitude'] = data.pop('lat', None)
    data['longitude'] = data.pop('lon', None)
    data['route_tag'] = data.pop('routetag', None)
    data['seconds_since_last_report'] = data.pop('secssincereport')
    return data

def vehicle_location(agency_tag, route_tag, epoch_time):
    url = urls.vehicle_location(agency_tag, route_tag, epoch_time)
    soup, encoding = utils.make_request(url)
    return [_vehicle_location(veh, encoding) for veh in soup.find_all('vehicle')]
