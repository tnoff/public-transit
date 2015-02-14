import httpretty
import unittest

from transit import client
from transit import utils

class TestClient(unittest.TestCase):

    def setUp(self):
        self.client = client.Client()

    @httpretty.activate
    def test_fails(self):
        # Check that failures catch nicely
        # Failure xml format in nextbus docs
        test_body = '''
        <body>
            <error>
                'God damnit mcnulty'
            </error>
        </body>
        '''
        test_url = 'http://carcettiformayor.org'
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=test_body,
                               content_type='application/xml')
        self.assertRaises(Exception, utils.make_request, test_url)

    @httpretty.activate
    def test_agency_list(self):
        # Check against example from offical docs
        test_body = '''
        <body>
            <agency tag="actransit" title="AC Transit, CA" regionTitle="California-Northern">
            <agency tag="alexandria" title="Alexandria DASH, VA" shortTitle="DASH" regionTitle="Virginia">
        </body>'''
        httpretty.register_uri(httpretty.GET,
                               'http://webservices.nextbus.com/service/publicXMLFeed?command=agencyList',
                               body=test_body,
                               content_type='application/xml')
        agency_list = self.client.agency_list()
        self.assertEqual(len(agency_list), 2)
        self.assertTrue('actransit' in [a.tag for a in agency_list])
        self.assertTrue('AC Transit, CA' in [a.title for a in agency_list])
        self.assertTrue('California-Northern' in [a.region for a in agency_list])

    @httpretty.activate
    def test_agency_search(self):
        # Check against example from offical docs
        test_body = '''
        <body>
            <agency tag="actransit" title="AC Transit, CA" regionTitle="California-Northern">
            <agency tag="alexandria" title="Alexandria DASH, VA" shortTitle="DASH" regionTitle="Virginia">
        </body>'''
        httpretty.register_uri(httpretty.GET,
                               'http://webservices.nextbus.com/service/publicXMLFeed?command=agencyList',
                               body=test_body,
                               content_type='application/xml')
        agency_list = self.client.agency_search('tag', 'ac')
        self.assertNotEqual(len(agency_list), 0)
        agency_list = self.client.agency_search('title', 'a')
        self.assertEqual(len(agency_list), 2)
        agency_list = self.client.agency_search('regiontitle', 'v')
        self.assertEqual(len(agency_list), 1)
        agency_list = self.client.agency_search('tag', 'afnoenfo')
        self.assertEqual(len(agency_list), 0)
        agency_list = self.client.agency_search('afeonfqoefn', 'afeon')
        self.assertEqual(len(agency_list), 0)

    @httpretty.activate
    def test_route_list(self):
        # Check against example from offical docs
        test_body = '''
        <body>
            <route tag="1" title="1-California" shortTitle="1-Calif">
            <route tag="3" title="3-Jackson" shortTitle="3-Jacksn">
        </body>
        '''
        httpretty.register_uri(httpretty.GET,
                               'http://webservices.nextbus.com/service/publicXMLFeed?command=routeList&a=sf-muni',
                               body=test_body,
                               content_type='application/xml')
        route_list = self.client.route_list('sf-muni')
        self.assertTrue(len(route_list), 2)
        self.assertTrue('1' in [r.tag for r in route_list])
        self.assertTrue('1-California' in [r.title for r in route_list])
        self.assertTrue('1-Calif' in [r.short_title for r in route_list])

    @httpretty.activate
    def test_route_show(self):
        # Check against example from official docs
        test_body = '''
        <body>
        <route tag="N" title="N-Judah" color="003399" oppositeColor="ffffff" latMin="37.7601699" latMax="37.7932299" lonMin="-122.5092" lonMax="-122.38798">
            <stop tag="KINGd4S0" title="King St and 4th St" shortTitle="King & 4th" lat="37.776036" lon="-122.394355" stopId="1"/>
            <stop tag="KINGd2S0" title="King St and 2nd St" shortTitle="King & 2nd" lat="37.7796152" lon="-122.3898067" stopId="2"/>
        </body>
        '''
        httpretty.register_uri(httpretty.GET,
                               'http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=sf-muni&r=N',
                               body=test_body,
                               content_type='application/xml')
        route = self.client.route_get('sf-muni', 'N')
        self.assertEqual('N', route.tag)
