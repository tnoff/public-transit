import httpretty
import unittest

from transit import client
from transit.exceptions import TransitException
from transit import utils
from transit import urls

from tests.data import agency_list as good_agency_list
from tests.data import error as good_error
from tests.data import route_config as good_route_config
from tests.data import route_list as good_route_list
from tests.data import stop_predictions as good_stop_predictions

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
                               body=good_error.text,
                               content_type='application/xml')
        self.assertRaises(TransitException, utils.make_request, test_url)

    @httpretty.activate
    def test_agency_list(self):
        test_url = urls.agency['list']
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=good_agency_list.text,
                               content_type='application/xml')
        agency_list = self.client.agency_list()
        self.assertEqual(len(agency_list), 64)
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
                               body=good_agency_list.text,
                               content_type='application/xml')
        agency_list = self.client.agency_search('tag', 'ac')
        self.assertNotEqual(len(agency_list), 0)
        agency_list = self.client.agency_search('title', 'a')
        self.assertEqual(len(agency_list), 59)
        agency_list = self.client.agency_search('regiontitle', 'v')
        self.assertEqual(len(agency_list), 6)
        agency_list = self.client.agency_search('tag', 'afnoenfo')
        self.assertEqual(len(agency_list), 0)
        agency_list = self.client.agency_search('afeonfqoefn', 'afeon')
        self.assertEqual(len(agency_list), 0)

    @httpretty.activate
    def test_route_list(self):
        test_url = urls.route['list'] % 'sf-muni'
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=good_route_list.text,
                               content_type='application/xml')
        route_list = self.client.route_list('sf-muni')
        self.assertEqual(len(route_list), 107)
        self.assertTrue('C' in [r.tag for r in route_list])
        self.assertTrue('C' in [r.title for r in route_list])
        self.assertEqual(route_list[0].short_title, None)
        # Should be at least one short title
        found_short_title = False
        for i in route_list:
            if i.short_title != None:
                found_short_title = True
                break
        self.assertTrue(found_short_title)

    @httpretty.activate
    def test_route_show(self):
        test_url = urls.route['show'] % ('actransit', '22')
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=good_route_config.text,
                               content_type='application/xml')
        route = self.client.route_get('sf-muni', 'N')
        self.assertEqual('22', route.tag)
        self.assertTrue(isinstance(route.latitude_min, float))
        self.assertTrue(len(route.stops), 2)
        self.assertTrue('0802410' in [s.tag for s in route.stops])
        self.assertTrue(isinstance(route.stops[0].stop_id, int))
        self.assertTrue(isinstance(route.stops[0].latitude, float))
        self.assertTrue(len(route.stops[0].directions), 2)
        self.assertTrue(len(route.stops[1].directions), 1)
        self.assertTrue(len(route.paths), 2)
        self.assertTrue(len(route.paths[0]), 2)

    @httpretty.activate
    def test_stop_prediction_no_route(self):
        test_url = urls.predictions['stop'] % ('actransit', '51303')
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=good_stop_predictions.text,
                               content_type='application/xml')
        predictions = self.client.stop_prediction('actransit', 51303)
        self.assertEqual(len(predictions), 3)
        self.assertEqual(len(predictions[0].predictions), 1)
        self.assertTrue('clockwise' in predictions[0].predictions[0].direction)
        self.assertTrue(isinstance(predictions[0].predictions[0].minutes, int))
        self.assertTrue(isinstance(predictions[0].predictions[0].seconds, int))
        self.assertEqual(len(predictions[2].predictions), 0)
        self.assertEqual(len(predictions[0].messages), 1)
        self.assertEqual(len(predictions[1].messages), 0)
