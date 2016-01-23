MAIN_URL = 'http://api.bart.gov/api/'
DEFAULT_KEY = 'MW9S-E7SL-26DU-VV8V'

# service urls
def service_advisory(date='today', key=DEFAULT_KEY):
    return MAIN_URL + 'bsa.aspx?cmd=bsa&key=%s&date=%s' % (key, date)

def train_count(key=DEFAULT_KEY):
    return MAIN_URL + 'bsa.aspx?cmd=count&key=%s' % key

def elevator_status(key=DEFAULT_KEY):
    return MAIN_URL + 'bsa.aspx?cmd=elev&key=%s' % key

# route urls
def route_list(key=DEFAULT_KEY, schedule=None, date=None):
    url = MAIN_URL + 'route.aspx?cmd=routes&key=%s' % key
    if schedule:
        url += '&sched=%s' % schedule
    if date:
        url += '&date=%s' % date
    return url

def route_info(route_number, schedule=None, date=None, key=DEFAULT_KEY):
    url = MAIN_URL + 'route.aspx?cmd=routeinfo&route=%s&key=%s' % \
        (route_number, key)
    if schedule:
        url += '&sched=%s' % schedule
    if date:
        url += '&date=%s' % date
    return url

# station urls
def station_info(station, key=DEFAULT_KEY):
    station = station.lower()
    url = MAIN_URL + 'stn.aspx?cmd=stninfo&orig=%s&key=%s' % (station, key)
    return url

def station_access(station, key=DEFAULT_KEY):
    station = station.lower()
    url = MAIN_URL + 'stn.aspx?cmd=stnaccess&orig=%s&key=%s' % (station, key)
    return url

def estimated_departures(station, platform=None, direction=None,
                         key=DEFAULT_KEY):
    url = MAIN_URL + 'etd.aspx?cmd=etd&orig=%s&key=%s' % (station, key)
    if platform:
        url += '&plat=%s' % platform
    if direction:
        url += '&dir=%s' % direction.lower()
    return url

def station_schedule(station, date=None, key=DEFAULT_KEY):
    station = station.lower()
    url = MAIN_URL + 'sched.aspx?cmd=stnsched&orig=%s&key=%s' % (station, key)
    if date:
        url += '&date=%s' % date
    return url

# schedule urls
def schedule_list(key=DEFAULT_KEY):
    url = MAIN_URL + 'sched.aspx?cmd=scheds&key=%s' % key
    return url

def schedule_fare(origin_station, destination_station, date=None,
                  schedule=None, key=DEFAULT_KEY):
    origin_station = origin_station.lower()
    destination_station = destination_station.lower()
    url = MAIN_URL + 'sched.aspx?cmd=fare&orig=%s&dest=%s&key=%s' % \
        (origin_station, destination_station, key)
    if date:
        url += '&date=%s' % date
    if schedule:
        url += '&sched=%s' % schedule
    return url
