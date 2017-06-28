MAIN_URL = 'http://api.bart.gov/api/'
DEFAULT_KEY = 'MW9S-E7SL-26DU-VV8V'

# service urls
def service_advisory(date='today', key=DEFAULT_KEY):
    return '%sbsa.aspx?cmd=bsa&key=%s&date=%s' % (MAIN_URL, key, date)

def train_count(key=DEFAULT_KEY):
    return '%sbsa.aspx?cmd=count&key=%s' % (MAIN_URL, key)

def elevator_status(key=DEFAULT_KEY):
    return '%sbsa.aspx?cmd=elev&key=%s' % (MAIN_URL, key)

# route urls
def route_list(key=DEFAULT_KEY, schedule=None, date=None):
    url = '%sroute.aspx?cmd=routes&key=%s' % (MAIN_URL, key)
    if schedule:
        url = '%s&sched=%s' % (url, schedule)
    if date:
        url = '%s&date=%s' % (url, date)
    return url

def route_info(route_number, schedule=None, date=None, key=DEFAULT_KEY):
    url = '%sroute.aspx?cmd=routeinfo&route=%s&key=%s' % \
        (MAIN_URL, route_number, key)
    if schedule:
        url = '%s&sched=%s' % (url, schedule)
    if date:
        url = '%s&date=%s' % (url, date)
    return url

# station urls
def station_info(station, key=DEFAULT_KEY):
    return '%sstn.aspx?cmd=stninfo&orig=%s&key=%s' % (MAIN_URL, station, key)

def station_access(station, key=DEFAULT_KEY):
    return '%sstn.aspx?cmd=stnaccess&orig=%s&key=%s' % (MAIN_URL, station, key)

def estimated_departures(station, platform=None, direction=None,
                         key=DEFAULT_KEY):
    url = '%setd.aspx?cmd=etd&orig=%s&key=%s' % (MAIN_URL, station, key)
    if platform:
        url = '%s&plat=%s' % (url, platform)
    if direction:
        url = '%s&dir=%s' % (url, direction)
    return url

def station_schedule(station, date=None, key=DEFAULT_KEY):
    url = '%ssched.aspx?cmd=stnsched&orig=%s&key=%s' % (MAIN_URL, station, key)
    if date:
        url = '%s&date=%s' % (url, date)
    return url

# schedule urls
def schedule_list(key=DEFAULT_KEY):
    return '%ssched.aspx?cmd=scheds&key=%s' % (MAIN_URL, key)

def schedule_fare(origin_station, destination_station, date=None,
                  schedule=None, key=DEFAULT_KEY):
    url = '%ssched.aspx?cmd=fare&orig=%s&dest=%s&key=%s' % \
        (MAIN_URL, origin_station, destination_station, key)
    if date:
        url = '%s&date=%s' % (url, date)
    if schedule:
        url = '%s&sched=%s' % (url, schedule)
    return url
