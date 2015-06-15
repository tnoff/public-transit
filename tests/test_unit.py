import httpretty
import unittest

from transit import client
from transit.exceptions import TransitException
from transit.common import urls, utils

from transit.modules import agency, route

from tests.data import agency_list as agency_list
from tests.data import error as error
from tests.data import message_get as message_get
from tests.data import message_get_multi as message_get_multi
from tests.data import multi_predict_one as multi_one
from tests.data import multi_predict_two as multi_two
from tests.data import route_show as route_show
from tests.data import route_list as route_list
from tests.data import schedule_get as schedule_get
from tests.data import stop_predictions as stop_predictions
from tests.data import stop_predictions_route as stop_predictions_route
from tests.data import vehicle_locations as vehicle_locations

class TestClient(unittest.TestCase):

    @httpretty.activate
    def test_fails(self):
        # Check that failures catch nicely
        # Failure xml format in nextbus docs
        test_url = urls.agency['list']
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=error.text,
                               content_type='application/xml')
        self.assertRaises(TransitException, utils.make_request, test_url)

    @httpretty.activate
    def test_agency_list(self):
        test_url = urls.agency['list']
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=agency_list.text,
                               content_type='application/xml')
        agencies = client.agency_list()
        # Make sure list generated correctly
        for a in agencies:
            self.assertTrue(isinstance(a, agency.Agency))
            self.assertNotEqual(None, a.tag)

    @httpretty.activate
    def test_route_list(self):
        agency_tag = 'sf-muni'
        test_url = urls.route['list'] % agency_tag
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=route_list.text,
                               content_type='application/xml')
        routes = client.route_list(agency_tag)
        for r in routes:
            self.assertTrue(isinstance(r, route.Route))
            self.assertNotEqual(r.route_tag, None)
            self.assertEqual(r.agency_tag, agency_tag)

    @httpretty.activate
    def test_route_show(self):
        agency_tag = 'actransit'
        route_tag = '22'
        test_url = urls.route['show'] % (agency_tag, route_tag)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=route_show.text,
                               content_type='application/xml')
        r = client.route_get(agency_tag, route_tag)
        self.assertEqual(r.agency_tag, agency_tag)
        self.assertEqual(r.route_tag, route_tag)
        self.assertNotEqual(len(r.stops), 0)
        self.assertNotEqual(len(r.directions), 0)
        self.assertNotEqual(len(r.directions[0].stop_tags), 0)
        self.assertNotEqual(len(r.paths), 0)

    @httpretty.activate
    def test_stop_prediction_no_route(self):
        agency_tag = 'actransit'
        stop_id = '51303'
        test_url = urls.predictions['stop'] % (agency_tag, stop_id)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=stop_predictions.text,
                               content_type='application/xml')
        preds = client.stop_prediction(agency_tag, stop_id)
        first_pred = preds[0]
        self.assertNotEqual(len(first_pred.directions), 0)
        self.assertNotEqual(len(first_pred.directions[0].predictions), 0)
        self.assertNotEqual(len(first_pred.messages), 0)

    @httpretty.activate
    def test_stop_prediction_with_route(self):
        agency_tag = 'actransit'
        stop_id = '51303'
        route_tag = '22'
        test_url = urls.predictions['route'] % \
            (agency_tag, stop_id, route_tag)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=stop_predictions_route.text,
                               content_type='application/xml')
        preds = client.stop_prediction(agency_tag, stop_id, route_tag=route_tag)
        first_pred = preds[0]
        self.assertNotEqual(len(first_pred.directions), 0)
        self.assertNotEqual(len(first_pred.directions[0].predictions), 0)

    @httpretty.activate
    def test_schedule(self):
        agency_tag = 'actransit'
        route_tag = '22'
        test_url = urls.schedule['show'] % (agency_tag, route_tag)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=schedule_get.text,
                               content_type='application/xml')
        schedules = client.schedule_get(agency_tag, route_tag)
        first_sched = schedules[0]
        self.assertNotEqual(len(first_sched.blocks), 0)
        first_block = first_sched.blocks[0]
        self.assertNotEqual(len(first_block.stop_schedules), 0)

    @httpretty.activate
    def test_vehicle_locations(self):
        agency_tag = 'sf-muni'
        route_tag = 'N'
        epoch_time = '1144953500233'
        test_url = urls.vehicle['location'] % \
            (agency_tag, route_tag, epoch_time)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=vehicle_locations.text,
                               content_type='application/xml')
        locations = client.vehicle_location(agency_tag, route_tag, epoch_time)
        self.assertNotEqual(len(locations), 0)

    @httpretty.activate
    def test_message_single(self):
        # Test with one arg
        agency_tag = 'sf-muni'
        route_tags = ['38']
        test_url = urls.message['message']['url'] % (agency_tag)
        for i in route_tags:
            test_url += urls.message['message']['suffix'] % i
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=message_get.text,
                               content_type='application/xml')
        routes = client.message_get(agency_tag, route_tags)
        first_route = routes[0]
        self.assertNotEqual(len(first_route.messages), 0)

    @httpretty.activate
    def test_message_multiple(self):
        # Test with mulitple args
        agency_tag = 'sf-muni'
        route_tags = ['38', '47']
        test_url = urls.message['message']['url'] % (agency_tag)
        for i in route_tags:
            test_url += urls.message['message']['suffix'] % i
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=message_get_multi.text,
                               content_type='application/xml')
        routes = client.message_get(agency_tag, route_tags)
        self.assertTrue(len(routes) > 1)
        first_route = routes[0]
        self.assertNotEqual(len(first_route.messages), 0)

    @httpretty.activate
    def test_multi_prediction_single(self):
        # Test with one stop/route
        agency_tag = 'sf-muni'
        data = {'38' : ['13568']}
        test_url = urls.predictions['multi']['url'] % (agency_tag)
        for key in data:
            for i in data[key]:
                test_url += urls.predictions['multi']['suffix'] % (key, i)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=multi_one.text,
                               content_type='application/xml')
        preds = client.multiple_stop_predictions(agency_tag, data)
        first_pred = preds[0]
        self.assertNotEqual(len(first_pred.directions), 0)
        self.assertNotEqual(len(first_pred.directions[0].predictions), 0)
        self.assertNotEqual(len(first_pred.messages), 0)

    @httpretty.activate
    def test_multi_prediction_multiple(self):
        # Test with multiple stops on same route
        agency_tag = 'sf-muni'
        data = {'38' : ['13568', '13567']}
        test_url = urls.predictions['multi']['url'] % ('sf-muni')
        for key in data:
            for i in data[key]:
                test_url += urls.predictions['multi']['suffix'] % (key, i)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=multi_two.text,
                               content_type='application/xml')
        preds = client.multiple_stop_predictions(agency_tag, data)
        first_pred = preds[0]
        self.assertNotEqual(len(first_pred.directions), 0)
        self.assertNotEqual(len(first_pred.directions[0].predictions), 0)
        self.assertNotEqual(len(first_pred.messages), 0)
