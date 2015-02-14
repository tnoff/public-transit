# Agency interface
from transit import urls
from transit import utils

class Agency(object):
    def __init__(self, tag, title, region):
        self.tag = tag
        self.title = title
        self.region = region

    def __str__(self):
        return '%s - %s - %s' % (self.title, self.region, self.tag)

class AgencyClient(object):
    def __init__(self):
        pass

    def list(self):
        '''Get list of agencies'''
        url = urls.agency['list']
        soup = utils.make_request(url)

        # Build agency list
        agency_list = []
        for agency in soup.find_all('agency'):
            agency_list.append(Agency(agency.get('tag'),
                                      agency.get('title'),
                                      agency.get('regionTitle')))
        return agency_list
