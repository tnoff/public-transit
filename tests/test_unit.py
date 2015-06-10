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
from tests.data import schedule_get as good_schedule_get
from tests.data import stop_predictions as good_stop_predictions
from tests.data import stop_predictions_route as good_stop_predictions_route
from tests.data import vehicle_locations as good_vehicle_locations

class TestClient(unittest.TestCase):

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
        client.agency_list()

    @httpretty.activate
    def test_agency_search(self):
        test_url = urls.agency['list']
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=good_agency_list.text,
                               content_type='application/xml')
        client.agency_search('tag', 'ac')

    @httpretty.activate
    def test_route_list(self):
        test_url = urls.route['list'] % 'sf-muni'
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=good_route_list.text,
                               content_type='application/xml')
        client.route_list('sf-muni')

    @httpretty.activate
    def test_route_show(self):
        test_url = urls.route['show'] % ('actransit', '22')
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=good_route_config.text,
                               content_type='application/xml')
        client.route_get('sf-muni', 'N')

    @httpretty.activate
    def test_stop_prediction_no_route(self):
        test_url = urls.predictions['stop'] % ('actransit', '51303')
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=good_stop_predictions.text,
                               content_type='application/xml')
        client.stop_prediction('actransit', 51303)

    @httpretty.activate
    def test_stop_prediction_with_route(self):
        test_url = urls.predictions['route'] % ('actransit', '51303', '22')
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=good_stop_predictions_route.text,
                               content_type='application/xml')
        client.stop_prediction('actransit', 51303)

    @httpretty.activate
    def test_schedule(self):
        test_url = urls.schedule['show'] % ('actransit', '22')
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=good_schedule_get.text,
                               content_type='application/xml')
        client.schedule_get('actransit', '22')

    @httpretty.activate
    def test_vehicle_locations(self):
        test_url = urls.vehicle['location'] % ('sf-muni', 'N', '1144953500233')
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=good_vehicle_locations.text,
                               content_type='application/xml')
        client.vehicle_location('sf-muni', 'N', '1144953500233')
