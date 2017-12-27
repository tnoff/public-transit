from transit import utils

def vehicle_location(vehicle_data, encoding):
    args = ['id', 'heading', 'lat', 'lon', 'routetag', 'secssincereport', 'speedkmhr',
            'predictable']
    data = utils.parse_page(vehicle_data, args, encoding)
    data['vehicle_id'] = data.pop('id', None)
    data['latitude'] = float(data.pop('lat', None))
    data['longitude'] = float(data.pop('lon', None))
    data['route_tag'] = data.pop('routetag', None)
    data['seconds_since_last_report'] = int(data.pop('secssincereport'))
    data['speed_km_hr'] = int(data.pop('speedkmhr'))
    data['predictable'] = data['predictable'] == 'true'
    return data
