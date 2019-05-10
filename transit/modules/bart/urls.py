MAIN_URL = 'http://api.bart.gov/api/'

# service urls
def service_advisory(bart_api_key, date='today'):
    return '%sbsa.aspx?cmd=bsa&key=%s&date=%s' % (MAIN_URL, bart_api_key, date)

def train_count(bart_api_key):
    return '%sbsa.aspx?cmd=count&key=%s' % (MAIN_URL, bart_api_key)

def elevator_status(bart_api_key):
    return '%sbsa.aspx?cmd=elev&key=%s' % (MAIN_URL, bart_api_key)

# route urls
def route_list(bart_api_key, schedule=None, date=None):
    url = '%sroute.aspx?cmd=routes&key=%s' % (MAIN_URL, bart_api_key)
    if schedule:
        url = '%s&sched=%s' % (url, schedule)
    if date:
        url = '%s&date=%s' % (url, date)
    return url

def route_info(route_number, bart_api_key, schedule=None, date=None):
    url = '%sroute.aspx?cmd=routeinfo&route=%s&key=%s' % \
        (MAIN_URL, route_number, bart_api_key)
    if schedule:
        url = '%s&sched=%s' % (url, schedule)
    if date:
        url = '%s&date=%s' % (url, date)
    return url

# station urls
def station_info(station, bart_api_key):
    return '%sstn.aspx?cmd=stninfo&orig=%s&key=%s' % (MAIN_URL,
                                                               station.lower(),
                                                               bart_api_key)

def station_access(station, bart_api_key):
    return '%sstn.aspx?cmd=stnaccess&orig=%s&key=%s' % (MAIN_URL,
                                                                 station.lower(),
                                                                 bart_api_key)

def estimated_departures(station, bart_api_key, platform=None, direction=None):
    url = '%setd.aspx?cmd=etd&orig=%s&key=%s' % (MAIN_URL, station.lower(), bart_api_key)
    if platform:
        url = '%s&plat=%s' % (url, platform)
    if direction:
        url = '%s&dir=%s' % (url, direction.lower())
    return url

def station_schedule(station, bart_api_key, date=None):
    url = '%ssched.aspx?cmd=stnsched&orig=%s&key=%s' % (MAIN_URL,
                                                                 station.lower(),
                                                                 bart_api_key)
    if date:
        url = '%s&date=%s' % (url, date)
    return url

# schedule urls
def schedule_list(bart_api_key):
    return '%ssched.aspx?cmd=scheds&key=%s' % (MAIN_URL, bart_api_key)

def schedule_fare(origin_station, destination_station, bart_api_key, date=None,
                  schedule=None):
    url = '%ssched.aspx?cmd=fare&orig=%s&dest=%s&key=%s' % \
        (MAIN_URL, origin_station.lower(), destination_station.lower(), bart_api_key)
    if date:
        url = '%s&date=%s' % (url, date)
    if schedule:
        url = '%s&sched=%s' % (url, schedule)
    return url
