# Agency interface
from transit import urls
from transit import utils

class Agency(object):
    def __init__(self, tag, title, region):
        self.tag = tag
        self.title = title
        self.region = region

    def __repr__(self):
        return '%s - %s - %s' % (self.title, self.region, self.tag)


class Route(object):
    def __init__(self, tag, title=None, short_title=None):
        self.tag = tag
        self.title = title
        self.short_title = short_title

    def __repr__(self):
        return '%s - %s' % (self.tag, self.title)

class Client(object):
    def __init__(self):
        pass

    def agency_list(self):
        '''Get list of agencies'''
        url = urls.agency['list']
        soup = utils.make_request(url)

        # Build agency list
        agency_list = []
        for agency in soup.find_all('agency'):
            agency_list.append(Agency(agency.get('tag'),
                                      agency.get('title'),
                                      agency.get('regiontitle')))
        return agency_list

    def route_list(self, agency_tag):
        '''List routes for agency'''
        url = urls.route['list'] % agency_tag
        soup = utils.make_request(url)

        # Build route list
        route_list = []
        for route in soup.find_all('route'):
            route_list.append(Route(route.get('tag'),
                                    title=route.get('title'),
                                    short_title=route.get('shorttitle')))
        return route_list
