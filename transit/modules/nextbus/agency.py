from transit.urls import nextbus
from transit.common import utils

from transit.modules.nextbus import route, schedule, stop, vehicle

class Agency(object):
    def __init__(self, agency_data):
        self.tag = agency_data.get('tag').encode('utf-8')
        self.title = agency_data.get('title').encode('utf-8')
        self.region = agency_data.get('regiontitle').encode('utf-8')

    def route_list(self):
        return route.route_list(self.tag)

    def route_get(self, route_tag):
        return route.route_get(self.tag, route_tag)

    def stop_prediction(self, stop_id, route_tag=None):
        return stop.stop_prediction(self.tag, stop_id, route_tag=route_tag)

    def multiple_stop_prediction(self, stop_data):
        return stop.multiple_stop_prediction(self.tag, stop_data)

    def schedule_get(self, route_tag):
        return schedule.schedule_get(self.tag, route_tag)

    def vehicle_location(self, route_tag, epoch_time):
        return vehicle.vehicle_location(self.tag, route_tag, epoch_time)

    def message_get(self, route_tags):
        return route.message_get(self.tag, route_tags)

    def __repr__(self):
        return '%s - %s - %s' % (self.title, self.region, self.tag)

def list_all():
    '''Get list of agencies'''
    url = nextbus.agency_list()
    soup = utils.make_request(url)
    return [Agency(i) for i in soup.find_all('agency')]
