# Agency interface
from transit import urls
from transit import utils

class Agency(object):
    def __init__(self, tag, title, region):
        self.tag = tag.encode('utf-8')
        self.title = title.encode('utf-8')
        self.region = region.encode('utf-8')

    def __repr__(self):
        return '%s - %s - %s' % (self.title, self.region, self.tag)


class Route(object):
    def __init__(self, tag, title, short_title,
                 color=None, opposite_color=None, latitude_min=None,
                 latitude_max=None, longitude_min=None, longitude_max=None):
        # Present Everywhere
        self.tag = tag.encode('utf-8')
        self.title = title.encode('utf-8')
        # Present only in route show or route list
        try:
            self.short_title = short_title.encode('utf-8')
        except AttributeError:
            self.short_title = None
        try:
            self.color = color.encode('utf-8')
        except AttributeError:
            self.color = None
        try:
            self.opposite_color = opposite_color.encode('utf-8')
        except AttributeError:
            self.opposite_color = None
        try:
            self.latitude_min = float(latitude_min.encode('utf-8'))
        except AttributeError:
            self.latitude_min = None
        try:
            self.latitude_max = float(latitude_max.encode('utf-8'))
        except AttributeError:
            self.lititude_max = None
        try:
            self.longitdue_min = float(longitude_min.encode('utf-8'))
        except AttributeError:
            self.longitdue_min = None
        try:
            self.longitude_max = float(longitude_max.encode('utf-8'))
        except AttributeError:
            self.longitude_max = None

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

    def agency_search(self, key, value):
        '''Search for agency with value in key'''
        url = urls.agency['list']
        soup = utils.make_request(url)

        # Search for agency, return list of matching
        agency_list = []
        nice_value = value.lower().replace(' ', '')
        nice_key = key.lower().replace(' ', '')
        for agency in soup.find_all('agency'):
            for key in agency.attrs.keys():
                if nice_key in key.encode('utf-8'):
                    search_value = agency.get(key).encode('utf-8').lower().replace(' ', '')
                    if nice_value in search_value:
                        agency_list.append(Agency(agency.get('tag'),
                                                  agency.get('title'),
                                                  agency.get('regiontitle')))
                        break
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

    def route_get(self, agency_tag, route_tag):
        '''Get route information'''
        url = urls.route['show'] % (agency_tag, route_tag)
        soup = utils.make_request(url)

        # Get route data
        r = soup.find('route')
        route = Route(r.get('tag'), title=r.get('title'),
                      short_title=r.get('shorttile'),
                      color=r.get('color'), opposite_color=r.get('opposite_color'),
                      latitude_min=r.get('latmin'), latitude_max=r.get('latmax'),
                      longitude_min=r.get('lonmin'), longitude_max=r.get('longmax'))
        return route
