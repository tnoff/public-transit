from transit import utils

def route(route_data, encoding):
    args = ['name', 'abbr', 'number', 'color', 'routeid']
    data = utils.parse_page(route_data, args, encoding)
    data['abbreviation'] = data.pop('abbr', None)
    # this is silly, it returns "ROUTE 1" instead of just int(1)
    route_id = data.pop('routeid')
    data['route_id'] = int(route_id.replace('ROUTE', ''))
    return data

def route_info(route_data, encoding):
    data = route(route_data, encoding)
    args = ['origin', 'destination', 'holidays', 'num_stns']
    additional_data = utils.parse_page(route_data, args, encoding)
    data.update(additional_data)
    data['holidays'] = int(data.pop('holidays', 0)) == 1
    data['stations'] = []
    for station in route_data.find_all('station'):
        data['stations'].append(utils.clean_value(station.contents[0], encoding))
    return data
