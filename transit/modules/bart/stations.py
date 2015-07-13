from transit.common import utils
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
    def __init__(self, station_data, encoding):
        self.name = utils.pretty_strip(station_data.find('name'),
                                       encoding)
        self.abbreviation = utils.pretty_strip(station_data.find('abbr'),
                                               encoding)

    def __repr__(self):
        return '%s' % self.name


class Station(StationBase):
    def __init__(self, station_data, encoding):
        StationBase.__init__(self, station_data, encoding)
        self.gtfs_latitude = float(utils.pretty_strip(station_data.find('gtfs_latitude'),
                                                      encoding))
        self.gtfs_longitude = float(utils.pretty_strip(station_data.find('gtfs_longitude'),
                                                       encoding))
        self.address = utils.pretty_strip(station_data.find('address'), encoding)
        self.city = utils.pretty_strip(station_data.find('county'), encoding)
        self.county = utils.pretty_strip(station_data.find('county'), encoding)
        self.state = utils.pretty_strip(station_data.find('state'), encoding)
        self.zipcode = utils.pretty_strip(station_data.find('zipcode'),
                                          encoding)
        self.platform_info = utils.pretty_strip(station_data.find('platform_info'),
                                                encoding)
        self.intro = utils.pretty_strip(station_data.find('intro'), encoding)
        self.cross_street = utils.pretty_strip(station_data.find('cross_street'),
                                               encoding)
        self.food = utils.pretty_strip(station_data.find('food'), encoding)
        self.shopping = utils.pretty_strip(station_data.find('shopping'),
                                           encoding)
        self.attraction = utils.pretty_strip(station_data.find('attraction'),
                                             encoding)
        self.link = utils.pretty_strip(station_data.find('link'), encoding)

        self.north_routes = []
        north_routes = station_data.find('north_routes')
        for route in north_routes.find_all('route'):
            route_string = utils.pretty_strip(route, encoding)
            self.north_routes.append(int(route_string.replace('ROUTE', '')))

        self.south_routes = []
        south_routes = station_data.find('south_routes')
        for route in south_routes.find_all('route'):
            route_string = utils.pretty_strip(route, encoding)
            self.south_routes.append(int(route_string.replace('ROUTE', '')))

        north_platforms = station_data.find('north_platforms')
        self.north_platforms = []
        for plat in north_platforms.find_all('platform'):
            self.north_platforms.append(int(utils.pretty_strip(plat, encoding)))

        south_platforms = station_data.find('south_platforms')
        self.south_platforms = []
        for plat in south_platforms.find_all('platform'):
            self.south_platforms.append(int(utils.pretty_strip(plat, encoding)))

class StationAccess(StationBase):
    def __init__(self, station_data, encoding):
        StationBase.__init__(self, station_data, encoding)
        self.parking_flag = station_data.get('parking_flag').encode(encoding) == 1
        self.bike_flag = station_data.get('bike_flag').encode(encoding) == 1
        self.bike_station_flag = station_data.get('bike_station_flag').encode(encoding) == 1
        self.locker_flag = station_data.get('locker_flag').encode(encoding) == 1

        # Bart returns html as a string here, yeah its dumb
        self.entering = utils.stupid_bart_bug(station_data.find('entering'),
                                              encoding)
        self.exiting = utils.stupid_bart_bug(station_data.find('exiting'),
                                             encoding)
        self.parking = utils.stupid_bart_bug(station_data.find('parking'),
                                             encoding)
        self.lockers = utils.stupid_bart_bug(station_data.find('lockers'),
                                             encoding)
        self.destinations = utils.stupid_bart_bug(station_data.find('destinations'),
                                                  encoding)
        self.transit_info = utils.stupid_bart_bug(station_data.find('transit_info'),
                                                  encoding)
        self.link = utils.pretty_strip(station_data.find('link'), encoding)

def station_list():
    return STATION_MAPPING

def station_info(station):
    url = bart.station_info(station)
    soup, encoding = utils.make_request(url)
    return Station(soup.find('station'), encoding)

def station_access(station, legend=False):
    url = bart.station_access(station, legend=legend)
    soup, encoding = utils.make_request(url)
    return StationAccess(soup.find('station'), encoding)
