from transit import utils

def vehicle_location(vehicle_data, encoding):
    args = ['id', 'heading', 'lat', 'lon', 'routetag', 'secssincereport', 'speedkmhr',
            'predictable']
    data = utils.parse_page(vehicle_data, args, encoding)
    data['vehicle_id'] = data.pop('id', None)
    data['latitude'] = data.pop('lat', None)
    data['longitude'] = data.pop('lon', None)
    data['route_tag'] = data.pop('routetag', None)
    data['seconds_since_last_report'] = data.pop('secssincereport')
    return data
