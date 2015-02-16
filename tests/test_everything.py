import httpretty
import unittest

from transit import client
from transit.exceptions import TransitException
from transit import utils
from transit import urls

from . import test_data

class TestClient(unittest.TestCase):

    def setUp(self):
        self.client = client.Client()

    @httpretty.activate
    def test_fails(self):
        # Check that failures catch nicely
        # Failure xml format in nextbus docs
        test_url = urls.agency['list']
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=test_data.error_page,
                               content_type='application/xml')
        self.assertRaises(TransitException, utils.make_request, test_url)

    @httpretty.activate
    def test_agency_list(self):
        test_url = urls.agency['list']
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=test_data.agency_list,
                               content_type='application/xml')
        agency_list = self.client.agency_list()
        self.assertEqual(len(agency_list), 14)
        # Test tag
        self.assertTrue('actransit' in [a.tag for a in agency_list])
        # Test title
        self.assertTrue('AC Transit' in [a.title for a in agency_list])
        # Test region title
        self.assertTrue('California-Northern' in [a.region for a in agency_list])
        # Test negative
        self.assertFalse('derp' in [a.tag for a in agency_list])
        self.assertFalse('DERP' in [a.title for a in agency_list])
        self.assertFalse('derp' in [a.region for a in agency_list])

    @httpretty.activate
    def test_agency_search(self):
        test_url = urls.agency['list']
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=test_data.agency_list,
                               content_type='application/xml')
        agency_list = self.client.agency_search('tag', 'ac')
        self.assertNotEqual(len(agency_list), 0)
        agency_list = self.client.agency_search('title', 'a')
        self.assertEqual(len(agency_list), 11)
        agency_list = self.client.agency_search('regiontitle', 'v')
        self.assertEqual(len(agency_list), 0)
        agency_list = self.client.agency_search('tag', 'afnoenfo')
        self.assertEqual(len(agency_list), 0)
        agency_list = self.client.agency_search('afeonfqoefn', 'afeon')
        self.assertEqual(len(agency_list), 0)

    @httpretty.activate
    def test_route_list(self):
        test_url = urls.route['list'] % 'sf-muni'
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=test_data.route_list,
                               content_type='application/xml')
        route_list = self.client.route_list('sf-muni')
        self.assertEqual(len(route_list), 14)
        self.assertTrue('C' in [r.tag for r in route_list])
        self.assertTrue('C' in [r.title for r in route_list])
        self.assertNotEqual(route_list[0].short_title, None)
        self.assertEqual(route_list[1].short_title, None)

    @httpretty.activate
    def test_route_show(self):
        # Check against example from official docs
        test_body = '''
        <body>
        <route tag="N" title="N-Judah" color="003399" oppositeColor="ffffff" latMin="37.7601699" latMax="37.7932299" lonMin="-122.5092" lonMax="-122.38798">
            <stop tag="KINGd4S0" title="King St and 4th St" shortTitle="King & 4th" lat="37.776036" lon="-122.394355" stopId="1"/>
            <stop tag="KINGd2S0" title="King St and 2nd St" shortTitle="King & 2nd" lat="37.7796152" lon="-122.3898067" stopId="2"/>
            <direction tag="out" title="Outbound to La Playa" name="Outbound" useForUI="true">
                <stop tag="KINGd4S0"/>
                <stop tag="KINGd2S0"/>
            </direction>
            <direction tag="in" title="Inbound to Caltrain" name="Inbound" useForUI="true">
                <stop tag="KINGd2S0"/>
            </direction>
            <path>
                <point lat="37.7695171" lon="-122.4287571"/>
                <point lat="37.7695099" lon="-122.42887"/>
            </path>
            <path>
                <point lat="37.77551" lon="-122.39513"/>
                <point lat="37.77449" lon="-122.39642"/>
                <point lat="37.77413" lon="-122.39687"/>
                <point lat="37.77385" lon="-122.39721"/>
            </path>
        </route>
        </body>
        '''
        httpretty.register_uri(httpretty.GET,
                               'http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=sf-muni&r=N',
                               body=test_body,
                               content_type='application/xml')
        route = self.client.route_get('sf-muni', 'N')
        self.assertEqual('N', route.tag)
        self.assertTrue(isinstance(route.latitude_min, float))
        self.assertTrue(len(route.stops), 2)
        self.assertTrue('KINGd4S0' in [s.tag for s in route.stops])
        self.assertTrue(isinstance(route.stops[0].stop_id, int))
        self.assertTrue(isinstance(route.stops[0].latitude, float))
        self.assertTrue(len(route.stops[0].directions), 2)
        self.assertTrue(len(route.stops[1].directions), 1)
        self.assertTrue(len(route.paths), 2)
        self.assertTrue(len(route.paths[0]), 2)

    @httpretty.activate
    def test_stop_prediction_no_route(self):
        test_body = '''
        <body>
        <predictions agencytitle="AC Transit" routetag="22" routetitle="22" stoptag="9902820" stoptitle="Mission Blvd &amp; Central Blvd">
            <direction title="Counterclockwise to Hayward BART">
                <prediction block="22001" dirtag="22_25_1" epochtime="1423954532475" isdeparture="false" minutes="35" seconds="2113" triptag="3972069" vehicle="1215"></prediction>
            </direction>
        </predictions>
        <predictions agencytitle="AC Transit" routetag="99" routetitle="99" stoptag="9902820" stoptitle="Mission Blvd &amp; Central Blvd">
            <direction title="To Bay Fair BART">
                <prediction block="99003" dirtag="99_72_1" epochtime="1423953067107" isdeparture="false" minutes="10" seconds="647" triptag="3972452" vehicle="1420"></prediction>
                <prediction block="99005" dirtag="99_72_1" epochtime="1423954396301" isdeparture="false" minutes="32" seconds="1976" triptag="3972453" vehicle="1412"></prediction>
                <prediction affectedbylayover="true" block="99002" dirtag="99_72_1" epochtime="1423956641402" isdeparture="false" minutes="70" seconds="4222" triptag="3972454" vehicle="1419"></prediction>
            </direction>
            <message text="something went wrong, dont panic" />
        </predictions>
        <predictions agencytitle="AC Transit" dirtitlebecausenopredictions="To Downtown Oakland" routetag="801" routetitle="801" stoptag="9902820" stoptitle="Mission Blvd &amp; Central Blvd">
        </predictions>
        </body>
        '''
        httpretty.register_uri(httpretty.GET,
                               'http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=actransit&stopId=51303',
                               body=test_body,
                               content_type='application/xml')
        predictions = self.client.stop_prediction('actransit', 51303)
        self.assertEqual(len(predictions), 3)
        self.assertEqual(len(predictions[0].predictions), 1)
        self.assertTrue('clockwise' in predictions[0].predictions[0].direction)
        self.assertTrue(isinstance(predictions[0].predictions[0].minutes, int))
        self.assertTrue(isinstance(predictions[0].predictions[0].seconds, int))
        self.assertEqual(len(predictions[2].predictions), 0)
        self.assertEqual(len(predictions[1].messages), 1)
        self.assertEqual(len(predictions[0].messages), 0)
