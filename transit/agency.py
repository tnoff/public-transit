from transit import urls
from transit import utils

from transit import route
from transit import stop

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

    def __repr__(self):
        return '%s - %s - %s' % (self.title, self.region, self.tag)

def list_all():
    '''Get list of agencies'''
    url = urls.agency['list']
    soup = utils.make_request(url)

    # Build agency list
    return [Agency(i) for i in soup.find_all('agency')]
