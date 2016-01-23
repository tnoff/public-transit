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
    '''Get vehicle location for route at time
       agency_tag: agency tag
       route_tag: route tag
       epoch_time: epoch time for locations
    '''
    assert isinstance(agency_tag, basestring), 'agency tag must be string type'
    assert isinstance(route_tag, basestring), 'route tag must be string type'
    assert isinstance(epoch_time, int), 'epoch time must be int type'
    url = urls.vehicle_location(agency_tag, route_tag, epoch_time)
    soup, encoding = utils.make_request(url)
    return [_vehicle_location(veh, encoding) for veh in soup.find_all('vehicle')]
