from datetime import datetime

from transit.common import utils as common_utils
from transit.modules.bart import urls, utils
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

def _station_info(station_data):
    data = {}
    args = ['name', 'abbr', 'gtfs_latitude', 'gtfs_longitude', 'address', 'city',
            'county', 'state', 'zipcode', 'platform_info', 'intro', 'cross_street',
            'food', 'shopping', 'attraction', 'link']
    for arg in args:
        value = common_utils.parse_data(station_data, arg)
        data[arg] = value
    data['abbreviation'] = data.pop('abbr', None)

    data['north_routes'] = []
    north_routes = station_data.find('north_routes')
    for route in north_routes.find_all('route'):
        route_string = route.contents[0]
        data['north_routes'].append(int(route_string.replace('ROUTE ', '')))

    data['south_routes'] = []
    south_routes = station_data.find('south_routes')
    for route in south_routes.find_all('route'):
        route_string = route.contents[0]
        data['south_routes'].append(int(route_string.replace('ROUTE', '')))

    north_platforms = station_data.find('north_platforms')
    data['north_platforms'] = []
    for plat in north_platforms.find_all('platform'):
        route_string = plat.contents[0]
        data['north_platforms'].append(int(route_string))

    south_platforms = station_data.find('south_platforms')
    data['south_platforms'] = []
    for plat in south_platforms.find_all('platform'):
        route_string = plat.contents[0]
        data['south_platforms'].append(int(route_string))
    return data

def _station_access(station_data):
    data = {}
    args = ['name', 'abbr', 'parking_flag', 'bike_flag', 'locker_flag',
            'entering', 'exiting', 'parking', 'lockers', 'destinations', 'transit_info',
            'link']
    for arg in args:
        value = common_utils.parse_data(station_data, arg)
        data[arg] = value
    data['abbreviation'] = data.pop('abbr', None)
    data['parking_flag'] = data.pop('parking_flag', 0) == 1
    data['bike_flag'] = data.pop('bike_flag', 0) == 1
    data['locker_flag'] = data.pop('locker_flag', 0) == 1
    return data

def _estimate(estimate_data):
    data = {}
    args = ['platform', 'direction', 'length', 'color', 'bikeflag']
    for arg in args:
        value = common_utils.parse_data(estimate_data, arg)
        data[arg] = value
    data['bike_flag'] = data.pop('bikeflag', 0) == 1
    value = common_utils.parse_data(estimate_data, 'minutes')
    if not isinstance(value, int) and 'leaving' in value.lower():
        value = 0
    data['minutes'] = value
    return data

def _direction_estimates(estimate_data, destinations=None):
    data = {}
    data['abbreviation'] = common_utils.parse_data(estimate_data, 'abbreviation')
    # if destinations given, check here if valid
    # .. if not valid give up now to save time
    if destinations and data['abbreviation'].lower() not in destinations:
        raise TransitException("Not valid destination:%s" % data['abbreviation'])
    data['name'] = common_utils.parse_data(estimate_data, 'destination')
    data['estimates'] = [_estimate(i) for i in estimate_data.find_all('estimate')]
    return data

def _station_departures(station_data, destinations=None):
    data = {}
    args = ['name', 'abbr']
    for arg in args:
        value = common_utils.parse_data(station_data, arg)
        data[arg] = value
    data['abbreviation'] = data.pop('abbr', None)
    data['directions'] = []
    # if exception was raised then direction not in destinations given
    # .. so skip and dont put it in list
    for i in station_data.find_all('etd'):
        try:
            data['directions'].append(_direction_estimates(i, destinations))
        except TransitException:
            continue
    return data

def _schedule_time(item_data):
    data = {}
    line = common_utils.parse_data(item_data, 'line')
    data['line'] = line.replace('ROUTE ', '')
    data['head_station'] = common_utils.parse_data(item_data,
                                                   'trainheadstation')
    value = common_utils.parse_data(item_data, 'origtime')
    data['origin_time'] = datetime.strptime(value, datetime_format)
    value = common_utils.parse_data(item_data, 'desttime')
    data['destination_time'] = datetime.strptime(value, datetime_format)
    data['train_index'] = common_utils.parse_data(item_data, 'trainidx')
    bike_flag = common_utils.parse_data(item_data, 'bikeflag')
    data['bike_flag'] = (bike_flag == 1)
    return data

def _station_schedule(station_data):
    data = {}
    args = ['name', 'abbr']
    for arg in args:
        value = common_utils.parse_data(station_data, arg)
        data[arg] = value
    data['abbreviation'] = data.pop('abbr', None)
    data['schedule_times'] = [_schedule_time(i) for i in station_data.find_all('item')]
    return data

def station_list():
    return STATION_MAPPING

def station_info(station):
    url = urls.station_info(station)
    soup, encoding = utils.make_request(url)
    return _station_info(soup.find('station'))

def station_access(station):
    url = urls.station_access(station)
    soup, encoding = utils.make_request(url)
    return _station_access(soup.find('station'))

def multiple_station_departures(station_data):
    url = urls.estimated_departures('all')
    soup, encoding = utils.make_request(url)
    # make all keys lower case
    keys = station_data.keys()
    for key in keys:
        if key.lower() == key:
            continue
        station_data[key.lower()] = station_data[key]
        del station_data[key]
    abbreviations = [i.lower() for i in station_data]
    full_data = []
    for i in soup.find_all('station'):
        abbr = i.find('abbr').string.encode(encoding).lower()
        if abbr in abbreviations:
            full_data.append(_station_departures(i, station_data[abbr]))
    return full_data

def station_departures(station, platform=None, direction=None,
                       destinations=None):
    url = urls.estimated_departures(station, platform=platform,
                                    direction=direction)
    soup, encoding = utils.make_request(url)
    # make destination lower input here to save time
    if destinations:
        destinations = [i.lower() for i in destinations]
    return [_station_departures(i, destinations) \
        for i in soup.find_all('station')]

def station_schedule(station, date=None):
    url = urls.station_schedule(station, date=date)
    soup, encoding = utils.make_request(url)
    return _station_schedule(soup.find('station'))
