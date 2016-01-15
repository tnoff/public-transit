from datetime import datetime

from transit.common import utils as common_utils
from transit.modules.bart import urls, utils

datetime_format = '%m/%d/%Y %I:%M %p'

def _schedule(schedule_data):
    data = {}
    data['id'] = common_utils.parse_data(schedule_data, 'id')
    value = common_utils.parse_data(schedule_data, 'effectivedate')
    data['effective_date'] = datetime.strptime(value, datetime_format)
    return data

def _schedule_fare(schedule_data):
    data = {}
    args = ['origin', 'destination', 'sched_num']
    for arg in args:
        value = common_utils.parse_data(schedule_data, arg)
        data[arg] = value
    data['schedule_number'] = int(data.pop('sched_num', None))
    trip_data = schedule_data.find('trip')
    data['fare'] = common_utils.parse_data(trip_data, 'fare')
    discount = trip_data.find('discount')
    data['discount'] = common_utils.parse_data(discount, 'clipper')
    return data

def schedule_list():
    url = urls.schedule_list()
    soup, encoding = utils.make_request(url)
    return [_schedule(i) for i in soup.find_all('schedule')]

def schedule_fare(origin_station, destination_station,
                  date=None, schedule=None):
    url = urls.schedule_fare(origin_station, destination_station,
                             date=date, schedule=schedule)
    soup, encoding = utils.make_request(url)
    return _schedule_fare(soup)
