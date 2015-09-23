from transit.common import utils as common_utils
from transit.modules.bart import urls, utils

class Schedule(object):
    def __init__(self, schedule_data, encoding):
        self.id = common_utils.parse_data(schedule_data, 'id', encoding)
        self.effective_date = common_utils.parse_data(schedule_data,
                                                      'effectivedate', encoding,
                                                      datetime_format='%m/%d/%Y %I:%M %p')
    def __repr__(self):
        return '%s - %s' % (self.id, self.effective_date)

class ScheduleFare(object):
    def __init__(self, data, encoding):
        self.origin = common_utils.parse_data(data, 'origin', encoding)
        self.destination = common_utils.parse_data(data, 'destination', encoding)
        self.schedule_number = common_utils.parse_data(data, 'sched_num', encoding)

        trip_data = data.find('trip')

        self.fare = common_utils.parse_data(trip_data, 'fare', encoding)

        discount = trip_data.find('discount')

        self.discount = common_utils.parse_data(discount, 'clipper', encoding)
    def __repr__(self):
        return '%s' % self.fare

def schedule_list():
    url = urls.schedule_list()
    soup, encoding = utils.make_request(url)
    return [Schedule(i, encoding) for i in soup.find_all('schedule')]

def schedule_fare(origin_station, destination_station,
                  date=None, schedule=None):
    url = urls.schedule_fare(origin_station, destination_station,
                             date=date, schedule=schedule)
    soup, encoding = utils.make_request(url)
    return ScheduleFare(soup, encoding)
