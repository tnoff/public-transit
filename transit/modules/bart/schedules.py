from datetime import datetime

from transit.modules.bart import urls, utils

class Schedule(object):
    def __init__(self, schedule_data, encoding):
        self.id = schedule_data.get('id').encode(encoding)
        effective_date = schedule_data.get('effectivedate').encode(encoding)
        self.effective_date = datetime.strptime(effective_date,
                                                "%m/%d/%Y %I:%M %p")
    def __repr__(self):
        return '%s - %s' % (self.id, self.effective_date)

class ScheduleFare(object):
    def __init__(self, data, encoding):
        self.origin = utils.pretty_strip(data.find('origin'), encoding)
        self.destination = utils.pretty_strip(data.find('destination'),
                                              encoding)
        self.schedule_number = int(utils.pretty_strip(data.find('sched_num'),
                                                      encoding))
        trip_data = data.find('trip')
        self.fare = utils.pretty_strip(trip_data.find('fare'), encoding)
        self.discount = utils.pretty_strip(trip_data.find('discount').find('clipper'),
                                           encoding)
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
