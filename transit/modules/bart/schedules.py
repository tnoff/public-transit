from datetime import datetime

from transit.common import utils
from transit.urls import bart

class Schedule(object):
    def __init__(self, schedule_data, encoding):
        self.id = schedule_data.get('id').encode(encoding)
        effective_date = schedule_data.get('effectivedate').encode(encoding)
        self.effective_date = datetime.strptime(effective_date,
                                                "%m/%d/%Y %I:%M %p")
    def __repr__(self):
        return '%s - %s' % (self.id, self.effective_date)

def schedule_list():
    url = bart.schedule_list()
    soup, encoding = utils.make_request(url)
    return [Schedule(i, encoding) for i in soup.find_all('schedule')]
