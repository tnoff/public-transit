main_url = 'http://api.bart.gov/api/'
default_key = 'MW9S-E7SL-26DU-VV8V'

def service_advisory(date='today', key=default_key):
    return main_url + 'bsa.aspx?cmd=bsa&key=%s&date=%s' % (key, date)

def train_count(key=default_key):
    return main_url + 'bsa.aspx?cmd=count&key=%s' % key

def elevator_status(key=default_key):
    return main_url + 'bsa.aspx?cmd=elev&key=%s' % key

def estimated_departures(station, platform=None, direction=None,
                         key=default_key):
    url = main_url + 'etd.aspx?cmd=etd&orig=%s&key=%s' % (station, key)
    if platform:
        url += '&plat=%s' % platform
    if direction:
        url += '&dir=%s' % direction
    return url

def current_routes(key=default_key, schedule=None, date=None):
    url = main_url + 'route.aspx?cmd=routes&key=%s' % key
    if schedule:
        url += '&sched=%s' % schedule
    if date:
        url += '&date=%s' % date
    return url

def route_info(route_number, schedule=None, date=None, key=default_key):
    url = main_url + 'route.aspx?cmd=routeinfo&route=%s&key=%s' % \
        (route_number, key)
    if schedule:
        url += '&sched=%s' % schedule
    if date:
        url += '&date=%s' % date
    return url

def station_info(station, key=default_key):
    url = main_url + 'stn.aspx?cmd=stninfo&orig=%s&key=%s' % (station, key)
    return url

def station_access(station, legend=False, key=default_key):
    # legend can be True or False
    url = main_url + 'stn.aspx?cmd=stnaccess&orig=%s&key=%s' % (station, key)
    if legend:
        url += '&l=1'
    return url

def schedule_list(key=default_key):
    url = main_url + 'sched.aspx?cmd=scheds&key=%s' % key
    return url
