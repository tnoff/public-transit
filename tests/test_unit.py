import httpretty
import unittest

from transit import client
from transit.exceptions import TransitException
from transit.common import urls, utils

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
        client.agency_list()

    @httpretty.activate
    def test_route_list(self):
        test_url = urls.route['list'] % 'sf-muni'
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=route_list.text,
                               content_type='application/xml')
        client.route_list('sf-muni')

    @httpretty.activate
    def test_route_show(self):
        test_url = urls.route['show'] % ('actransit', '22')
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=route_show.text,
                               content_type='application/xml')
        client.route_get('sf-muni', 'N')

    @httpretty.activate
    def test_stop_prediction_no_route(self):
        test_url = urls.predictions['stop'] % ('actransit', '51303')
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=stop_predictions.text,
                               content_type='application/xml')
        client.stop_prediction('actransit', 51303)

    @httpretty.activate
    def test_stop_prediction_with_route(self):
        test_url = urls.predictions['route'] % ('actransit', '51303', '22')
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=stop_predictions_route.text,
                               content_type='application/xml')
        client.stop_prediction('actransit', 51303)

    @httpretty.activate
    def test_schedule(self):
        test_url = urls.schedule['show'] % ('actransit', '22')
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=schedule_get.text,
                               content_type='application/xml')
        client.schedule_get('actransit', '22')

    @httpretty.activate
    def test_vehicle_locations(self):
        test_url = urls.vehicle['location'] % ('sf-muni', 'N', '1144953500233')
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=vehicle_locations.text,
                               content_type='application/xml')
        client.vehicle_location('sf-muni', 'N', '1144953500233')

    @httpretty.activate
    def test_message(self):
        # Test with one arg
        test_url = urls.message['message']['url'] % ('sf-muni')
        tags = ['38']
        for i in tags:
            test_url += urls.message['message']['suffix'] % i
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=message_get.text,
                               content_type='application/xml')
        client.message_get('sf-muni', '38')
        # Test with mulitple args
        test_url = urls.message['message']['url'] % ('sf-muni')
        tags = ['38', '47']
        for i in tags:
            test_url += urls.message['message']['suffix'] % i
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=message_get_multi.text,
                               content_type='application/xml')
        client.message_get('sf-muni', ['38', '47'])

    @httpretty.activate
    def test_multi_prediction(self):
        # Test with one stop/route
        test_url = urls.predictions['multi']['url'] % ('sf-muni')
        data = {'38' : ['13568']}
        for key in data:
            for i in data[key]:
                test_url += urls.predictions['multi']['suffix'] % (key, i)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=multi_one.text,
                               content_type='application/xml')
        client.multiple_stop_predictions('sf-muni', data)
        # Test with multiple stops on same route
        test_url = urls.predictions['multi']['url'] % ('sf-muni')
        data = {'38' : ['13568', '13567']}
        for key in data:
            for i in data[key]:
                test_url += urls.predictions['multi']['suffix'] % (key, i)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=multi_two.text,
                               content_type='application/xml')
        client.multiple_stop_predictions('sf-muni', data)
