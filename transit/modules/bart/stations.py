from transit.common import utils as common_utils
from transit.exceptions import TransitException

datetime_format = '%I:%M %p'

# bart doesnt have a way to call this easily that I can find
# .. the one on their official website didnt include the new(-ish) station
# .. at Oakland Airport, so I assume it isnt maintained
STATION_MAPPING = {
    "12th" : "12th St. Oakland City Center",
    "16th" : "16th St. Mission (SF)",
    "19th" : "19th St. Oakland",
    "24th" : "24th St. Mission (SF)",
    "ashb" : "Ashby (Berkeley)",
    "balb" : "Balboa Park (SF)",
    "bayf" : "Bay Fair (San Leandro)",
    "cast" : "Castro Valley",
    "civc" : "Civic Center (SF)",
    "cols" : "Coliseum/Oakland Airport",
    "colm" : "Colma",
    "conc" : "Concord",
    "daly" : "Daly City",
    "dbrk" : "Downtown Berkeley",
    "dubl" : "Dublin/Pleasanton",
    "deln" : "El Cerrito del Norte",
    "plza" : "El Cerrito Plaza",
    "embr" : "Embarcadero (SF)",
    "frmt" : "Fremont",
    "ftvl" : "Fruitvale (Oakland)",
    "glen" : "Glen Park (SF)",
    "hayw" : "Hayward",
    "lafy" : "Lafayette",
    "lake" : "Lake Merritt (Oakland)",
    "mcar" : "MacArthur (Oakland)",
    "mlbr" : "Millbrae",
    "mont" : "Montgomery St. (SF)",
    "nbrk" : "North Berkeley",
    "ncon" : "North Concord/Martinez",
    "oakl" : "Oakland Int'l Airport",
    "orin" : "Orinda",
    "pitt" : "Pittsburg/Bay Point",
    "phil" : "Pleasant Hill",
    "powl" : "Powell St. (SF)",
    "rich" : "Richmond",
    "rock" : "Rockridge (Oakland)",
    "sbrn" : "San Bruno",
    "sfia" : "San Francisco Int'l Airport",
    "sanl" : "San Leandro",
    "shay" : "South Hayward",
    "ssan" : "South San Francisco",
    "ucty" : "Union City",
    "wcrk" : "Walnut Creek",
    "wdub" : "West Dublin",
    "woak" : "West Oakland",
}

# what is in the station object will differ on the call
# this base class has the very basic stuff that should be in all

def station_info(station_data, encoding):
    args = ['name', 'abbr', 'gtfs_latitude', 'gtfs_longitude', 'address', 'city',
            'county', 'state', 'zipcode', 'platform_info', 'intro', 'cross_street',
            'food', 'shopping', 'attraction', 'link']
    data = common_utils.parse_page(station_data, args, encoding)
    data['abbreviation'] = data.pop('abbr', None)

    data['north_routes'] = []
    north_routes = station_data.find('north_routes')
    for route in north_routes.find_all('route'):
        route_string = common_utils.clean_value(route.contents[0], encoding)
        data['north_routes'].append(int(route_string.replace('ROUTE ', '')))

    data['south_routes'] = []
    south_routes = station_data.find('south_routes')
    for route in south_routes.find_all('route'):
        route_string = common_utils.clean_value(route.contents[0], encoding)
        data['south_routes'].append(int(route_string.replace('ROUTE', '')))

    north_platforms = station_data.find('north_platforms')
    data['north_platforms'] = []
    for plat in north_platforms.find_all('platform'):
        route_string = common_utils.clean_value(plat.contents[0], encoding)
        data['north_platforms'].append(int(route_string))

    south_platforms = station_data.find('south_platforms')
    data['south_platforms'] = []
    for plat in south_platforms.find_all('platform'):
        route_string = common_utils.clean_value(plat.contents[0], encoding)
        data['south_platforms'].append(int(route_string))
    return data

def station_access(station_data, encoding):
    args = ['name', 'abbr', 'parking_flag', 'bike_flag', 'locker_flag',
            'entering', 'exiting', 'parking', 'lockers', 'destinations', 'transit_info',
            'link']
    data = common_utils.parse_page(station_data, args, encoding)
    data['abbreviation'] = data.pop('abbr', None)
    data['parking_flag'] = data.pop('parking_flag', 0) == 1
    data['bike_flag'] = data.pop('bike_flag', 0) == 1
    data['locker_flag'] = data.pop('locker_flag', 0) == 1
    return data

def estimate(estimate_data, encoding):
    args = ['platform', 'direction', 'length', 'color', 'bikeflag', 'minutes']
    data = common_utils.parse_page(estimate_data, args, encoding)
    data['bike_flag'] = data.pop('bikeflag', 0) == 1
    if not isinstance(data['minutes'], int) and 'leaving' in data['minutes'].lower():
        data['minutes'] = 0
    return data

def direction_estimates(estimate_data, encoding, destinations=None):
    data = common_utils.parse_page(estimate_data, ['abbreviation'], encoding)
    # if destinations given, check here if valid
    # .. if not valid give up now to save time
    if destinations and data['abbreviation'].lower() not in destinations:
        raise TransitException("Not valid destination:%s" % data['abbreviation'])
    new_data = common_utils.parse_page(estimate_data, ['destination'], encoding)
    data['name'] = new_data.pop('destination', None)
    data['estimates'] = []
    for est in estimate_data.find_all('estimate'):
        estimate_data = estimate(est, encoding)
        data['estimates'].append(estimate_data)
    return data

def station_departures(station_data, encoding, station_output=None):
    args = ['name', 'abbr']
    data = common_utils.parse_page(station_data, args, encoding)
    data['abbreviation'] = data.pop('abbr', None)
    destinations = None
    if station_output:
        try:
            destinations = station_output[data['abbreviation'].lower()]
        except KeyError:
            raise TransitException("%s not in accepted stations" % data['abbreviation'].lower())

    data['directions'] = []
    # if exception was raised then direction not in destinations given
    # .. so skip and dont put it in list
    for etd in station_data.find_all('etd'):
        try:
            direction_data = direction_estimates(etd, encoding, destinations=destinations)
            data['directions'].append(direction_data)
        except TransitException:
            continue
    return data

def schedule_time(schedule_data, encoding):
    args = ['line', 'trainheadstation', 'origtime', 'desttime', 'trainidx',
            'bikeflag']
    data = common_utils.parse_page(schedule_data, args, encoding,
                                   datetime_format=datetime_format)
    data['line'] = int(data.pop('line', '0').replace('ROUTE ', ''))
    data['head_station'] = data.pop('trainheadstation', None)
    data['origin_time'] = data.pop('origtime', None)
    data['destination_time'] = data.pop('desttime', None)
    data['train_index'] = int(data.pop('trainidx', None))
    bike_flag = int(data.pop('bikeflag', 0))
    data['bike_flag'] = bike_flag == 1
    return data

def station_schedule(station_data, encoding):
    args = ['name', 'abbr']
    data = common_utils.parse_page(station_data, args, encoding)
    data['abbreviation'] = data.pop('abbr', None)
    data['schedule_times'] = []
    for item in station_data.find_all('item'):
        data['schedule_times'].append(schedule_time(item, encoding))
    return data
