from transit.exceptions import TransitException
from transit.common import utils as common_utils
from transit.modules.bart import urls, utils

def _schedule(schedule_data, encoding):
    args = ['id', 'effectivedate']
    data = common_utils.parse_page(schedule_data, args, encoding)
    data['effective_date'] = data.pop('effectivedate', None)
    return data

def _schedule_fare(schedule_data, encoding):
    args = ['origin', 'destination', 'sched_num']
    data = common_utils.parse_page(schedule_data, args, encoding)
    data['schedule_number'] = data.pop('sched_num', None)

    # this page is a little strange, this is within another part
    trip_data = schedule_data.find('trip')
    fare_value = common_utils.parse_data(trip_data, 'fare')
    data['fare'] = common_utils.clean_value(fare_value, encoding)
    discount = trip_data.find('discount')
    clipper = common_utils.parse_data(discount, 'clipper')
    data['discount'] = common_utils.clean_value(clipper, encoding)
    return data

def schedule_list():
    '''List bart schedules'''
    url = urls.schedule_list()
    soup, encoding = utils.make_request(url)
    schedules = []
    for sched in soup.find_all('schedule'):
        sched_data = _schedule(sched, encoding)
        schedules.append(sched_data)
    return schedules

def schedule_fare(origin_station, destination_station,
                  date=None, schedule=None):
    '''Get the scheduled fare
        origin_station: station you'll onbard at
        destination_station: station you'll offboard at
        schedule: schedule number
        date: mm/dd/yyyy format
    '''
    assert isinstance(origin_station, basestring), 'origin station must be string type'
    assert isinstance(destination_station, basestring), 'destination station must be string type'
    assert schedule is None or isinstance(schedule, int),\
        'schedule number must be int or None type'
    if date and not utils.DATE_MATCH.match(date):
        raise TransitException('date must match pattern:%s' % utils.DATE_MATCH_REGEX)
    url = urls.schedule_fare(origin_station, destination_station,
                             date=date, schedule=schedule)
    soup, encoding = utils.make_request(url)
    return _schedule_fare(soup, encoding)
