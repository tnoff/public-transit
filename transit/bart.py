from datetime import datetime

from bs4 import BeautifulSoup
import requests

from transit.exceptions import TransitException, SkipException
from transit import utils

from transit.modules.bart import urls
from transit.modules.bart import advisories
from transit.modules.bart import routes
from transit.modules.bart import schedules
from transit.modules.bart import stations

def _make_request(url, markup="html.parser"):
    headers = {'accept-encoding' : 'gzip, deflate'}
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        raise TransitException("URL:%s does not return 200" % url)

    soup = BeautifulSoup(r.text, markup)
    # Get encoding from top of XML data
    contents = soup.contents
    while True:
        if str(contents[0]) == '\n':
            del contents[0]
        else:
            break
    encoding = str(soup.contents[0].split('encoding')[1])
    encoding = encoding.lstrip('="').rstrip('"')
    # check for errors
    error = soup.find('error')
    if error:
        error_string = error.string
        if not error_string:
            # bart gives error in "text" and "details"
            error_string1 = error.find('text').string.encode(encoding)
            error_string2 = error.find('details').string.encode(encoding)
            error_string = '%s:%s' % (error_string1, error_string2)
        raise TransitException(error_string)
    return soup, encoding

def _check_datetime(datetime_str):
    try:
        datetime.strptime(datetime_str, '%m/%d/%Y')
    except ValueError:
        raise TransitException("Datetime string invalid:%s" % datetime_str)

def service_advisory():
    '''
    System wide service advisory
    '''
    url = urls.service_advisory()
    soup, encoding = _make_request(url)
    service_advisories = []
    for bsa in soup.find_all('bsa'):
        service_data = advisories.service_advisory(bsa, encoding)
        service_advisories.append(service_data)
    return service_advisories

def train_count():
    '''
    System wide train count
    '''
    url = urls.train_count()
    soup, encoding = _make_request(url)
    return int(soup.find('traincount').string.encode(encoding))

def elevator_status():
    '''
    System wide elevator status
    '''
    url = urls.elevator_status()
    soup, encoding = _make_request(url)
    return advisories.service_advisory(soup.find('bsa'), encoding)

def route_list(schedule=None, date=None):
    '''
    Show information for specific route
    schedule    :   schedule number
    date        :   mm/dd/yyyy format
    '''
    assert schedule is None or isinstance(schedule, int),\
        'schedule number must be int or null type'
    assert date is None or isinstance(date, basestring), \
        'date must be string or null type'
    if date is not None:
        _check_datetime(date)
    url = urls.route_list(schedule=schedule, date=date)
    soup, encoding = _make_request(url)

    route_data = {}
    schedule_number = utils.parse_data(soup, 'sched_num')
    route_data['schedule_number'] = int(schedule_number)

    route_data['routes'] = []
    for route_xml in soup.find_all('route'):
        route_data['routes'].append(routes.route(route_xml, encoding))
    return route_data

def route_info(route_number, schedule=None, date=None):
    '''
    Show information for specific route
    route_number    :   number of route to show
    schedule        :   schedule number
    date            :   mm/dd/yyyy format
    '''
    assert isinstance(route_number, int), 'route number must be int type'
    assert schedule is None or isinstance(schedule, int),\
        'schedule number must be int or None type'
    assert date is None or isinstance(date, basestring), \
        'date must be string or null type'
    if date is not None:
        _check_datetime(date)
    url = urls.route_info(route_number, schedule=schedule, date=date)
    soup, encoding = _make_request(url)
    return routes.route_info(soup.find('route'), encoding)

def schedule_list():
    '''
    List bart schedules
    '''
    url = urls.schedule_list()
    soup, encoding = _make_request(url)
    new_schedules = []
    for sched in soup.find_all('schedule'):
        new_schedules.append(schedules.schedule(sched, encoding))
    return new_schedules

def schedule_fare(origin_station, destination_station,
                  date=None, schedule=None):
    '''
    Get the scheduled fare
    origin_station          :   station you'll onbard at
    destination_station     :   station you'll offboard at
    schedule                :   schedule number
    date                    :   mm/dd/yyyy format
    '''
    assert isinstance(origin_station, basestring), 'origin station must be string type'
    assert isinstance(destination_station, basestring), 'destination station must be string type'
    assert schedule is None or isinstance(schedule, int),\
        'schedule number must be int or None type'
    assert date is None or isinstance(date, basestring), \
        'date must be string or null type'
    if date is not None:
        _check_datetime(date)
    url = urls.schedule_fare(origin_station, destination_station,
                             date=date, schedule=schedule)
    soup, encoding = _make_request(url)
    return schedules.schedule_fare(soup, encoding)

def station_list():
    '''
    List all bart stations
    '''
    return stations.STATION_MAPPING

def station_info(station):
    '''
    Station information
    station     :   station abbreviation
    '''
    assert isinstance(station, basestring), 'station must be string type'
    url = urls.station_info(station)
    soup, encoding = _make_request(url)
    return stations.station_info(soup.find('station'), encoding)

def station_access(station):
    '''
    Station Access information
    station     :   station abbreviation
    '''
    assert isinstance(station, basestring), 'station must be string type'
    url = urls.station_access(station)
    soup, encoding = _make_request(url)
    return stations.station_access(soup.find('station'), encoding)

def station_departures(station, platform=None, direction=None,
                       destinations=None):
    '''
    Get estimated station departures
    station     :   station abbreviation
    plaform     :   platfrom number
    direction   :   (n)orth or (s)outh
    destinatons :   List of abbreviated destinations, exclude all others
    '''
    assert isinstance(station, basestring), 'station must be string type'
    assert platform is None or isinstance(platform, int),\
        'platform must be int or null type'
    assert direction is None or isinstance(direction, basestring),\
        'direction must be string or null type'
    assert destinations is None or isinstance(destinations, list), \
        'destinations must be list or null type'
    url = urls.estimated_departures(station, platform=platform,
                                    direction=direction)
    soup, encoding = _make_request(url)

    station = station.lower()
    if station == 'all':
        station_output = None
    elif destinations is not None:
        station_output = {station : [dest.lower() for dest in destinations]}
    else:
        station_output = {station : []}

    departs = []
    for station_data in soup.find_all('station'):
        departs.append(stations.station_departures(station_data, encoding,
                                                   station_output=station_output))
    return departs

def station_schedule(station, date=None):
    '''
    Get a stations schedule
    station     :   station abbreviation
    date        :   mm/dd/yyyy format
    '''
    assert isinstance(station, basestring), 'station must be string type'
    assert date is None or isinstance(date, basestring), \
        'date must be string or null type'
    if date is not None:
        _check_datetime(date)
    url = urls.station_schedule(station, date=date)
    soup, encoding = _make_request(url)
    return stations.station_schedule(soup.find('station'), encoding)

def station_multiple_departures(station_output):
    '''
    Get estimated departures for mutliple stations
    station_output:
        {
            'station_abbrevation' : [destination1, destination2],
            'station_abbreviation2' : [],
            # empty for all possible destinations
        }
    '''
    assert isinstance(station_output, dict), 'station output must be dict type'
    for key in station_output.keys():
        assert isinstance(key, basestring), 'station output keys must be stringtype'
        assert isinstance(station_output[key], list),\
            'station output values must be list type'
        for item in station_output[key]:
            assert isinstance(item, basestring),\
                'destination list item must be basestring type'
        station_data = station_output.pop(key)
        directions = [direct.lower() for direct in station_data]
        station_output[key.lower()] = directions

    # call a list of all departures here, then strip data for only stations requested
    url = urls.estimated_departures('all')
    soup, encoding = _make_request(url)
    full_data = []
    for station in soup.find_all('station'):
        try:
            full_data.append(stations.station_departures(station, encoding,
                                                         station_output=station_output))
        except SkipException:
            continue
    return full_data
