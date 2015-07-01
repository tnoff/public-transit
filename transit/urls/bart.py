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
