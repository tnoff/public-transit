from datetime import datetime

from transit.urls import nextbus
from transit.common import utils

class ScheduleRoute(object):
    def __init__(self, schedule_data, encoding):
        self.tag = schedule_data.get('tag').encode(encoding)
        self.title = schedule_data.get('title').encode(encoding)
        self.schedule_class = schedule_data.get('scheduleclass').encode(encoding)
        self.service_class = schedule_data.get('serviceclass').encode(encoding)
        self.direction = schedule_data.get('direction').encode(encoding)
        self.blocks = []

    def __repr__(self):
        return '%s - %s - %s' % (self.tag, self.direction, self.service_class)

class ScheduleBlock(object):
    def __init__(self, block_data, encoding):
        self.block_id = block_data.get('blockid').encode(encoding)
        self.stop_schedules = []

    def __repr__(self):
        return '%s' % self.block_id

class StopSchedule(object):
    def __init__(self, stop_data, encoding, title=None):
        self.stop_tag = stop_data.get('tag').encode(encoding)
        self.epoch_time = stop_data.get("epochtime").encode(encoding)
        time_data = stop_data.contents[0].encode(encoding)
        self.title = title
        if time_data == "--":
            self.time = None
        else:
            self.time = datetime.strptime(time_data, "%H:%M:%S")

    def __repr__(self):
        return '%s - %s' % (self.stop_tag, self.time)

def schedule_get(agency_tag, route_tag):
    url = nextbus.schedule_get(agency_tag, route_tag)
    soup, encoding = utils.make_request(url)

    new_route_list = []
    for new_route in soup.find_all('route'):
        sr = ScheduleRoute(new_route, encoding)
        # titles are put in the header for some reason
        # data: {tag: title, ...}
        title_data = dict()
        header = new_route.find('header')
        for new_stop in header.find_all('stop'):
            title_data[new_stop.get('tag').encode(encoding)] = \
                new_stop.contents[0].encode(encoding)
        for block in new_route.find_all('tr'):
            b = ScheduleBlock(block, encoding)
            for new_stop in block.find_all('stop'):
                ss = StopSchedule(new_stop, encoding)
                ss.title = title_data[ss.stop_tag]
                b.stop_schedules.append(ss)
            sr.blocks.append(b)
        new_route_list.append(sr)
    return new_route_list