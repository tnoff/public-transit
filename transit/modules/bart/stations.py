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

class StationBase(object):
    def __init__(self, data, encoding):
        self.name = common_utils.parse_data(data, 'name', encoding)
        self.abbreviation = common_utils.parse_data(data, 'abbr', encoding)

    def station_info(self):
        return station_info(self.abbreviation)

    def station_access(self):
        return station_access(self.abbreviation)

    def station_departures(self, platform=None, direction=None):
        return station_departures(self.abbreviation, platform=platform,
                                  direction=direction)

    def station_schedule(self, date=None):
        return station_schedule(self.abbreviation, date=date)

    def __repr__(self):
        return '%s' % self.name


class StationInfo(StationBase): #pylint: disable=too-many-instance-attributes
    def __init__(self, data, encoding):
        StationBase.__init__(self, data, encoding)
        self.gtfs_latitude = common_utils.parse_data(data, 'gtfs_latitude', encoding)
        self.gtfs_longitude = common_utils.parse_data(data, 'gtfs_longitude', encoding)
        self.address = common_utils.parse_data(data, 'address', encoding)
        self.city = common_utils.parse_data(data, 'city', encoding)
        self.county = common_utils.parse_data(data, 'county', encoding)
        self.state = common_utils.parse_data(data, 'state', encoding)
        self.zipcode = common_utils.parse_data(data, 'zipcode', encoding)
        self.platform_info = common_utils.parse_data(data, 'platform_info', encoding)
        self.intro = common_utils.parse_data(data, 'intro', encoding)
        self.cross_street = common_utils.parse_data(data, 'cross_street', encoding)
        self.food = common_utils.parse_data(data, 'food', encoding)
        self.shopping = common_utils.parse_data(data, 'shopping', encoding)
        self.attraction = common_utils.parse_data(data, 'attraction', encoding)
        self.link = common_utils.parse_data(data, 'link', encoding)

        self.north_routes = []
        north_routes = data.find('north_routes')
        for route in north_routes.find_all('route'):
            route_string = route.contents[0].encode(encoding)
            self.north_routes.append(int(route_string.replace('ROUTE ', '')))

        self.south_routes = []
        south_routes = data.find('south_routes')
        for route in south_routes.find_all('route'):
            route_string = route.contents[0].encode(encoding)
            self.south_routes.append(int(route_string.replace('ROUTE', '')))

        north_platforms = data.find('north_platforms')
        self.north_platforms = []
        for plat in north_platforms.find_all('platform'):
            route_string = plat.contents[0].encode(encoding)
            self.north_platforms.append(int(route_string))

        south_platforms = data.find('south_platforms')
        self.south_platforms = []
        for plat in south_platforms.find_all('platform'):
            route_string = plat.contents[0].encode(encoding)
            self.south_platforms.append(int(route_string))

class StationAccess(StationBase): #pylint: disable=too-many-instance-attributes
    def __init__(self, data, encoding):
        StationBase.__init__(self, data, encoding)
        parking_flag = common_utils.parse_data(data, 'parking_flag', encoding)
        self.parking_flag = (parking_flag == 1)
        bike_flag = common_utils.parse_data(data, 'bike_flag', encoding)
        self.bike_flag = (bike_flag == 1)
        locker_flag = common_utils.parse_data(data, 'locker_flag', encoding)
        self.locker_flag = (locker_flag == 1)

        self.entering = common_utils.parse_data(data, 'entering', encoding)
        self.exiting = common_utils.parse_data(data, 'exiting', encoding)
        self.parking = common_utils.parse_data(data, 'parking', encoding)
        self.lockers = common_utils.parse_data(data, 'lockers', encoding)
        self.destinations = common_utils.parse_data(data, 'destinations', encoding)
        self.transit_info = common_utils.parse_data(data, 'transit_info', encoding)
        self.link = common_utils.parse_data(data, 'link', encoding)


class Estimate(object):
    def __init__(self, estimate_data, encoding):
        self.minutes = common_utils.parse_data(estimate_data, 'minutes', encoding)
        if not isinstance(self.minutes, int) and 'leaving' in self.minutes.lower():
            self.minutes = 0
        self.platform = common_utils.parse_data(estimate_data, 'platform', encoding)
        self.direction = common_utils.parse_data(estimate_data, 'direction', encoding)
        self.length = common_utils.parse_data(estimate_data, 'length', encoding)
        self.color = common_utils.parse_data(estimate_data, 'color', encoding)
        bike_flag = common_utils.parse_data(estimate_data, 'bikeflag', encoding)
        self.bike_flag = (bike_flag == 1)

    def __repr__(self):
        return '%s minutes' % self.minutes

class DirectionEstimates(object):
    def __init__(self, data, encoding, destinations):
        self.abbreviation = common_utils.parse_data(data, 'abbreviation', encoding)
        # if destinations given, check here if valid
        # .. if not valid give up now to save time
        if destinations:
            if self.abbreviation.lower() not in destinations:
                raise TransitException("Not valid destination:%s" % self.abbreviation)
        self.name = common_utils.parse_data(data, 'destination', encoding)
        self.estimates = \
            [Estimate(i, encoding) for i in data.find_all('estimate')]

    def __repr__(self):
        return '%s - %s' % (self.name, self.estimates)

class StationDepartures(StationBase):
    def __init__(self, data, encoding, destinations=None):
        StationBase.__init__(self, data, encoding)
        self.directions = []
        # if exception was raised then direction not in destinations given
        # .. so skip and dont put it in list
        for i in data.find_all('etd'):
            try:
                self.directions.append(DirectionEstimates(i, encoding, destinations))
            except TransitException:
                continue

    def __repr__(self):
        return '%s - %s' % (self.name, self.directions)

class ScheduleTime(object):
    def __init__(self, item_data, encoding):
        line = common_utils.parse_data(item_data, 'line', encoding)
        self.line = line.replace('ROUTE ', '')
        self.head_station = common_utils.parse_data(item_data,
                                                    'trainheadstation', encoding)
        self.origin_time = common_utils.parse_data(item_data, 'origtime',
                                                   encoding,
                                                   datetime_format=datetime_format)
        self.destination_time = common_utils.parse_data(item_data, 'desttime',
                                                        encoding,
                                                        datetime_format=datetime_format)
        self.train_index = common_utils.parse_data(item_data, 'trainidx', encoding)
        bike_flag = common_utils.parse_data(item_data, 'bikeflag', encoding)
        self.bike_flag = (bike_flag == 1)

class StationSchedule(StationBase):
    def __init__(self, data, encoding):
        StationBase.__init__(self, data, encoding)
        self.schedule_times = [ScheduleTime(i, encoding) \
            for i in data.find_all('item')]

def station_list():
    return STATION_MAPPING

def station_info(station):
    url = urls.station_info(station)
    soup, encoding = utils.make_request(url)
    return StationInfo(soup.find('station'), encoding)

def station_access(station):
    url = urls.station_access(station)
    soup, encoding = utils.make_request(url)
    return StationAccess(soup.find('station'), encoding)

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
            full_data.append(StationDepartures(i, encoding, station_data[abbr]))
    return full_data

def station_departures(station, platform=None, direction=None,
                       destinations=None):
    url = urls.estimated_departures(station, platform=platform,
                                    direction=direction)
    soup, encoding = utils.make_request(url)
    # make destination lower input here to save time
    if destinations:
        destinations = [i.lower() for i in destinations]
    return [StationDepartures(i, encoding, destinations) \
        for i in soup.find_all('station')]

def station_schedule(station, date=None):
    url = urls.station_schedule(station, date=date)
    soup, encoding = utils.make_request(url)
    return StationSchedule(soup.find('station'), encoding)
