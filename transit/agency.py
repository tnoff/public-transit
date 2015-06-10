from transit import urls
from transit import utils

class Agency(object):
    def __init__(self, agency_data):
        self.tag = agency_data.get('tag').encode('utf-8')
        self.title = agency_data.get('title').encode('utf-8')
        self.region = agency_data.get('regiontitle').encode('utf-8')

    def __repr__(self):
        return '%s - %s - %s' % (self.title, self.region, self.tag)

def list_all():
    '''Get list of agencies'''
    url = urls.agency['list']
    soup = utils.make_request(url)

    # Build agency list
    return [Agency(i) for i in soup.find_all('agency')]
