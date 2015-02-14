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
        test_body = '''
        <body>
            <error>
                Sheeeeeeeeeeeeeeeeeeeeeeeeeeeit -- Clay Davis
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
