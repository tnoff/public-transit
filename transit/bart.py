from bs4 import BeautifulSoup
from jsonschema import validate
import requests

from transit.exceptions import TransitException, SkipException
from transit import schema, utils

from transit.modules.bart import advisories, routes
from transit.modules.bart import schedules, stations, urls
from transit.modules.bart.settings import DATE_REGEX, STATION_REGEX

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

def service_advisory(bart_api_key):
    '''
    System wide service advisory

    bart_api_key : Use api key for request
    '''
    url = urls.service_advisory(bart_api_key)
    soup, encoding = _make_request(url)
    service_advisories = []
    for bsa in soup.find_all('bsa'):
        service_data = advisories.service_advisory(bsa, encoding)
        service_advisories.append(service_data)
    return service_advisories

def train_count(bart_api_key):
    '''
    System wide train count

    bart_api_key : Use api key for request
    '''
    url = urls.train_count(bart_api_key)
    soup, encoding = _make_request(url)
    return int(soup.find('traincount').string.encode(encoding))

def elevator_status(bart_api_key):
    '''
    System wide elevator status

    bart_api_key : Use api key for request
    '''
    url = urls.elevator_status(bart_api_key)
    soup, encoding = _make_request(url)
    return advisories.service_advisory(soup.find('bsa'), encoding)

def route_list(bart_api_key, schedule=None, date=None):
    '''
    Show information for specific route

    bart_api_key    :   Use api key for request
    schedule        :   Schedule number
    date            :   Date in MM/DD/YYY format
    '''
    utils.check_args(schedule, [int], allow_none=True)
    utils.check_args(date, [str], allow_none=True, regex=DATE_REGEX)
    url = urls.route_list(bart_api_key, schedule=schedule, date=date)
    soup, encoding = _make_request(url)

    route_data = {}
    schedule_number = utils.parse_data(soup, 'sched_num')
    route_data['schedule_number'] = int(schedule_number)

    route_data['routes'] = []
    for route_xml in soup.find_all('route'):
        route_data['routes'].append(routes.route(route_xml, encoding))
    return route_data

def route_info(route_number, bart_api_key, schedule=None, date=None):
    '''
    Show information for specific route

    route_number    :   Route number
    bart_api_key    :   Use api key for request
    schedule        :   Schedule number
    date            :   Date in MM/DD/YYYY format
    '''
    utils.check_args(route_number, [int])
    utils.check_args(schedule, [int], allow_none=True)
    utils.check_args(date, [str], allow_none=True, regex=DATE_REGEX)
    url = urls.route_info(route_number, bart_api_key, schedule=schedule, date=date)
    soup, encoding = _make_request(url)
    return routes.route_info(soup.find('route'), encoding)

def schedule_list(bart_api_key):
    '''
    List bart schedules

    bart_api_key : Use api key for request
    '''
    url = urls.schedule_list(bart_api_key)
    soup, encoding = _make_request(url)
    new_schedules = []
    for sched in soup.find_all('schedule'):
        new_schedules.append(schedules.schedule(sched, encoding))
    return new_schedules

def schedule_fare(origin_station, destination_station, bart_api_key,
                  date=None, schedule=None):
    '''
    Get the scheduled fare

    origin_station          :   Station you'll onbard at
    destination_station     :   Station you'll offboard at
    bart_api_key            :   Use api key for request
    schedule                :   Schedule number
    date                    :   Date in MM/DD/YYYY format
    '''
    utils.check_args(origin_station, [str], regex=STATION_REGEX)
    utils.check_args(destination_station, [str], regex=STATION_REGEX)
    utils.check_args(schedule, [int], allow_none=True)
    utils.check_args(date, [str], allow_none=True, regex=DATE_REGEX)
    url = urls.schedule_fare(origin_station, destination_station,
                             bart_api_key, date=date, schedule=schedule)
    soup, encoding = _make_request(url)
    return schedules.schedule_fare(soup, encoding)

def station_list(bart_api_key): #pylint:disable=unused-argument
    '''
    List all bart stations

    bart_api_key : Use api key for request
    '''
    # We dont need api key here, but have arg
    # So everything is uniform
    return stations.STATION_MAPPING

def station_info(station, bart_api_key):
    '''
    Station information

    station         :   Station abbreviation
    bart_api_key    :   Use api key for request
    '''
    utils.check_args(station, [str], regex=STATION_REGEX)
    url = urls.station_info(station, bart_api_key)
    soup, encoding = _make_request(url)
    return stations.station_info(soup.find('station'), encoding)

def station_access(station, bart_api_key):
    '''
    Station Access information

    station         :   Station abbreviation
    bart_api_key    :   Use api key for request
    '''
    utils.check_args(station, [str], regex=STATION_REGEX)
    url = urls.station_access(station, bart_api_key)
    soup, encoding = _make_request(url)
    return stations.station_access(soup.find('station'), encoding)

def station_departures(station, bart_api_key, platform=None, direction=None,
                       destinations=None):
    '''
    Get estimated station departures

    station         :   Station abbreviation
    bart_api_key    :   Use api key for request
    plaform         :   Platfrom number
    direction       :   (n)orth or (s)outh
    destinatons     :   List of abbreviated destinations, exclude all others
    '''
    utils.check_args(station, [str], regex=STATION_REGEX)
    utils.check_args(platform, [int], allow_none=True)
    utils.check_args(direction, [str], allow_none=True, regex="^[nsNS]$")
    utils.check_args(destinations, [str], allow_none=True, is_list=True,
                     regex=STATION_REGEX)
    url = urls.estimated_departures(station, bart_api_key, platform=platform,
                                    direction=direction)
    soup, encoding = _make_request(url)

    if station == 'all':
        station_output = None
    elif destinations is not None:
        station_output = {station : destinations}
    else:
        station_output = {station : []}

    departs = []
    for station_data in soup.find_all('station'):
        departs.append(stations.station_departures(station_data, encoding,
                                                   station_output=station_output))
    return departs

def station_schedule(station, bart_api_key, date=None):
    '''
    Get a stations schedule

    station         :   Station abbreviation
    bart_api_key    :   Use api key for request
    date            :   Date in MM/DD/YYYY format
    '''
    utils.check_args(station, [str], regex=STATION_REGEX)
    utils.check_args(date, [str], allow_none=True, regex=DATE_REGEX)
    url = urls.station_schedule(station, bart_api_key, date=date)
    soup, encoding = _make_request(url)
    return stations.station_schedule(soup.find('station'), encoding)

def station_multiple_departures(station_input, bart_api_key):
    '''
    Get estimated departures for mutliple stations
    station_input:
        {
            'station_abbrevation' : [destination1, destination2],
            'station_abbreviation2' : [],
            # empty for all possible destinations
        }
    bart_api_key : Use api key for request
    '''
    validate(station_input, schema.BART_MULTIPLE_STOP_SCHEMA)
    # call a list of all departures here, then strip data for only stations requested
    url = urls.estimated_departures('all', bart_api_key)
    soup, encoding = _make_request(url)
    full_data = []
    for station in soup.find_all('station'):
        try:
            full_data.append(stations.station_departures(station, encoding,
                                                         station_output=station_input))
        except SkipException:
            continue
    return full_data
