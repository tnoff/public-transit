from transit.common import utils as common_utils
from transit.modules.bart import urls, utils

datetime_format = '%m/%d/%Y %I:%M %p'

def _schedule(schedule_data, encoding):
    data = {}
    args = ['id', 'effectivedate']
    for arg in args:
        value = common_utils.parse_data(schedule_data, arg)
        data[arg] = common_utils.clean_value(value, encoding)
    data['effective_date'] = data.pop('effectivedate', None)
    return data

def _schedule_fare(schedule_data, encoding):
    data = {}
    args = ['origin', 'destination', 'sched_num']
    for arg in args:
        value = common_utils.parse_data(schedule_data, arg)
        data[arg] = common_utils.clean_value(value, encoding)
    data['schedule_number'] = data.pop('sched_num', None)
    # this page is a little strange, this is within another part
    trip_data = schedule_data.find('trip')
    #data['fare'] = common_utils.parse_data(trip_data, 'fare')
    fare_value = common_utils.parse_data(trip_data, 'fare')
    data['fare'] = common_utils.clean_value(fare_value, encoding)
    discount = trip_data.find('discount')
    clipper = common_utils.parse_data(discount, 'clipper')
    data['discount'] = common_utils.clean_value(clipper, encoding)
    return data

def schedule_list():
    url = urls.schedule_list()
    soup, encoding = utils.make_request(url)
    schedules = []
    for sched in soup.find_all('schedule'):
        sched_data = _schedule(sched, encoding)
        schedules.append(sched_data)
    return schedules

def schedule_fare(origin_station, destination_station,
                  date=None, schedule=None):
    url = urls.schedule_fare(origin_station, destination_station,
                             date=date, schedule=schedule)
    soup, encoding = utils.make_request(url)
    return _schedule_fare(soup, encoding)
