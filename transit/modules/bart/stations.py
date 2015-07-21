from datetime import datetime

from transit.common import utils
from transit.exceptions import TransitException
from transit.urls import bart

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
        self.name = utils.pretty_strip(data.find('name'),
                                       encoding)
        self.abbreviation = utils.pretty_strip(data.find('abbr'),
                                               encoding)

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
        self.gtfs_latitude = float(utils.pretty_strip(data.find('gtfs_latitude'),
                                                      encoding))
        self.gtfs_longitude = float(utils.pretty_strip(data.find('gtfs_longitude'),
                                                       encoding))
        self.address = utils.pretty_strip(data.find('address'), encoding)
        self.city = utils.pretty_strip(data.find('county'), encoding)
        self.county = utils.pretty_strip(data.find('county'), encoding)
        self.state = utils.pretty_strip(data.find('state'), encoding)
        self.zipcode = utils.pretty_strip(data.find('zipcode'),
                                          encoding)
        self.platform_info = utils.pretty_strip(data.find('platform_info'),
                                                encoding)
        self.intro = utils.pretty_strip(data.find('intro'), encoding)
        self.cross_street = utils.pretty_strip(data.find('cross_street'),
                                               encoding)
        self.food = utils.pretty_strip(data.find('food'), encoding)
        self.shopping = utils.pretty_strip(data.find('shopping'),
                                           encoding)
        self.attraction = utils.pretty_strip(data.find('attraction'),
                                             encoding)
        self.link = utils.pretty_strip(data.find('link'), encoding)

        self.north_routes = []
        north_routes = data.find('north_routes')
        for route in north_routes.find_all('route'):
            route_string = utils.pretty_strip(route, encoding)
            self.north_routes.append(int(route_string.replace('ROUTE', '')))

        self.south_routes = []
        south_routes = data.find('south_routes')
        for route in south_routes.find_all('route'):
            route_string = utils.pretty_strip(route, encoding)
            self.south_routes.append(int(route_string.replace('ROUTE', '')))

        north_platforms = data.find('north_platforms')
        self.north_platforms = []
        for plat in north_platforms.find_all('platform'):
            self.north_platforms.append(int(utils.pretty_strip(plat, encoding)))

        south_platforms = data.find('south_platforms')
        self.south_platforms = []
        for plat in south_platforms.find_all('platform'):
            self.south_platforms.append(int(utils.pretty_strip(plat, encoding)))

class StationAccess(StationBase): #pylint: disable=too-many-instance-attributes
    def __init__(self, data, encoding):
        StationBase.__init__(self, data, encoding)
        self.parking_flag = data.get('parking_flag').encode(encoding) == 1
        self.bike_flag = data.get('bike_flag').encode(encoding) == 1
        bike_flag = data.get('bike_station_flag').encode(encoding)
        self.bike_station_flag = int(bike_flag) == 1
        self.locker_flag = data.get('locker_flag').encode(encoding) == 1

        # Bart returns html as a string here, yeah its dumb
        self.entering = utils.stupid_bart_bug(data.find('entering'),
                                              encoding)
        self.exiting = utils.stupid_bart_bug(data.find('exiting'),
                                             encoding)
        self.parking = utils.stupid_bart_bug(data.find('parking'),
                                             encoding)
        self.lockers = utils.stupid_bart_bug(data.find('lockers'),
                                             encoding)
        self.destinations = utils.stupid_bart_bug(data.find('destinations'),
                                                  encoding)
        self.transit_info = utils.stupid_bart_bug(data.find('transit_info'),
                                                  encoding)
        self.link = utils.pretty_strip(data.find('link'), encoding)

class Estimate(object):
    def __init__(self, estimate_data, encoding):
        try:
            minutes = utils.pretty_strip(estimate_data.find('minutes'),
                                         encoding)
            self.minutes = int(minutes)
        except ValueError:
            # Most likely "Leaving"
            self.minutes = 0
        additional_keys = ['direction', 'length', 'color']
        self.platform = int(utils.pretty_strip(estimate_data.find('platform'),
                                               encoding))
        for key in additional_keys:
            setattr(self, key, utils.pretty_strip(estimate_data.find(key),
                                                  encoding))
        # True/False but given as 1/0
        self.bike_flag = int(utils.pretty_strip(estimate_data.find('bikeflag'),
                                                encoding)) == 1

    def __repr__(self):
        return '%s minutes' % self.minutes

class DirectionEstimates(object):
    def __init__(self, data, encoding, destinations):
        self.name = utils.pretty_strip(data.find('destination'),
                                                         encoding)
        self.abbreviation = utils.pretty_strip(data.find('abbreviation'),
                                               encoding)
        # if destinations given, check here if valid
        # .. if not valid give up now to save time
        if destinations:
            if self.abbreviation.lower() not in destinations:
                raise TransitException("Not valid destination:%s" % self.abbreviation)
        self.estimates = \
            [Estimate(i, encoding) for i in data.find_all('estimate')]

    def __repr__(self):
        return '%s - %s' % (self.name, self.estimates)

class StationDepartures(StationBase):
    def __init__(self, data, encoding, destinations):
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
    def __init__(self, item_data, _):
        self.line = int(item_data.get('line').replace('ROUTE ', ''))
        self.destination = item_data.get('trainheadstation')
        self.origin_time = datetime.strptime(item_data.get('origtime'),
                                             "%I:%M %p")
        self.destination_time = datetime.strptime(item_data.get('desttime'),
                                                  "%I:%M %p")
        self.train_index = int(item_data.get('trainidx'))
        self.bike_flag = int(item_data.get('bikeflag')) == 1

class StationSchedule(StationBase):
    def __init__(self, data, encoding):
        StationBase.__init__(self, data, encoding)
        self.schedule_times = [ScheduleTime(i, encoding) \
            for i in data.find_all('item')]

def station_list():
    return STATION_MAPPING

def station_info(station):
    url = bart.station_info(station)
    soup, encoding = utils.make_request(url)
    return StationInfo(soup.find('station'), encoding)

def station_access(station):
    url = bart.station_access(station)
    soup, encoding = utils.make_request(url)
    return StationAccess(soup.find('station'), encoding)

def station_departures(station, platform=None, direction=None,
                       destinations=None):
    url = bart.estimated_departures(station, platform=platform,
                                    direction=direction)
    soup, encoding = utils.make_request(url)
    # make destination lower input here to save time
    if destinations:
        destinations = [i.lower() for i in destinations]
    return [StationDepartures(i, encoding, destinations) \
        for i in soup.find_all('station')]

def station_schedule(station, date=None):
    url = bart.station_schedule(station, date=date)
    soup, encoding = utils.make_request(url)
    return StationSchedule(soup.find('station'), encoding)
