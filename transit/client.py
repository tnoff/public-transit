# Agency interface
from transit import urls
from transit import utils

class Agency(object):
    def __init__(self, tag, title, region):
        self.tag = str(tag)
        self.title = str(title)
        self.region = str(region)

    def __repr__(self):
        return '%s - %s - %s' % (self.title, self.region, self.tag)


class Route(object):
    def __init__(self, tag, title=None, short_title=None,
                 color=None, opposite_color=None, latitude_min=None,
                 latitude_max=None, longitude_min=None, longitude_max=None):
        self.tag = str(tag)
        self.title = str(title)
        self.short_title = str(short_title)
        self.color = str(color)
        self.opposite_color = str(opposite_color)
        self.latitude_min = float(latitude_min)
        self.latitude_max = float(latitude_max)
        self.longitdue_min = float(longitude_min)
        self.longitude_max = float(longitude_max)

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
        for agency in soup.find_all('agency'):
            if value.lower().replace(' ', '') in agency.get(key).lower().replace(' ', ''):
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

    def route_get(self, agency_tag, route_tag):
        '''Get route information'''
        print agency_tag, route_tag
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
