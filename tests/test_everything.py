import httpretty
import unittest

from transit import client

class TestAgency(unittest.TestCase):

    def setUp(self):
        self.client = client.Client()

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
