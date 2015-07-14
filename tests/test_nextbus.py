import httpretty

from transit import client
from transit.exceptions import TransitException
from transit.urls import nextbus
from transit.common import utils as common_utils

from tests import utils
from tests.data.nextbus import agency_list as agency_list
from tests.data.nextbus import error as error
from tests.data.nextbus import message_get as message_get
from tests.data.nextbus import message_get_multi as message_get_multi
from tests.data.nextbus import multi_predict_one as multi_one
from tests.data.nextbus import multi_predict_two as multi_two
from tests.data.nextbus import route_show as route_show
from tests.data.nextbus import route_list as route_list
from tests.data.nextbus import schedule_get as schedule_get
from tests.data.nextbus import stop_predictions as stop_predictions
from tests.data.nextbus import stop_predictions_route as stop_predictions_route
from tests.data.nextbus import vehicle_locations as vehicle_locations

class NextBusTestClient(utils.BaseTestClient):

    @httpretty.activate
    def test_fails(self):
        # Check that failures catch nicely
        # Failure xml format in nextbus docs
        test_url = nextbus.agency_list()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=error.text,
                               content_type='application/xml')
        self.assertRaises(TransitException, common_utils.make_request, test_url)

    @httpretty.activate
    def test_agency_list(self):
        test_url = nextbus.agency_list()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=agency_list.text,
                               content_type='application/xml')
        agencies = client.nextbus.agency_list()
        # Make sure list generated correctly
        for a in agencies:
            self.assert_all_variables(a)

    @httpretty.activate
    def test_route_list(self):
        agency_tag = 'sf-muni'
        test_url = nextbus.route_list(agency_list)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=route_list.text,
                               content_type='application/xml')
        routes = client.nextbus.route_list(agency_tag)
        for r in routes:
            self.assert_all_variables(r)

    @httpretty.activate
    def test_route_show(self):
        agency_tag = 'actransit'
        route_tag = '22'
        test_url = nextbus.route_show(agency_tag, route_tag)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=route_show.text,
                               content_type='application/xml')
        r = client.nextbus.route_get(agency_tag, route_tag)
        self.assert_all_variables(r)
        stop = r.stops[0]
        self.assert_all_variables(stop, skip=['short_title'])
        direction = r.directions[0]
        self.assert_all_variables(direction)
        tag = direction.stop_tags[0]
        self.assertTrue(isinstance(tag, str))
        path = r.paths[0]
        path_point = path[0]
        self.assert_all_variables(path_point)

    @httpretty.activate
    def test_stop_prediction_no_route(self):
        agency_tag = 'actransit'
        stop_id = '51303'
        test_url = nextbus.stop_prediction(agency_tag, stop_id)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=stop_predictions.text,
                               content_type='application/xml')
        preds = client.nextbus.stop_prediction(agency_tag, stop_id)
        first_pred = preds[0]
        self.assert_all_variables(first_pred)
        direction = first_pred.directions[0]
        self.assert_all_variables(direction)
        pred = direction.predictions[0]
        self.assert_all_variables(pred)

    @httpretty.activate
    def test_stop_prediction_with_route(self):
        agency_tag = 'actransit'
        stop_id = '51303'
        route_tag = '22'
        test_url = nextbus.stop_prediction(agency_tag, stop_id,
                                           route_tag=route_tag)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=stop_predictions_route.text,
                               content_type='application/xml')
        preds = client.nextbus.stop_prediction(agency_tag, stop_id,
                                               route_tag=route_tag)
        first_pred = preds[0]
        self.assert_all_variables(first_pred, skip=['messages'])
        direction = first_pred.directions[0]
        self.assert_all_variables(direction)
        pred = direction.predictions[0]
        self.assert_all_variables(pred)

    @httpretty.activate
    def test_schedule(self):
        agency_tag = 'actransit'
        route_tag = '22'
        test_url = nextbus.schedule_get(agency_tag, route_tag)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=schedule_get.text,
                               content_type='application/xml')
        schedules = client.nextbus.schedule_get(agency_tag, route_tag)
        first_sched = schedules[0]
        self.assert_all_variables(first_sched)
        first_block = first_sched.blocks[0]
        self.assert_all_variables(first_block)

    @httpretty.activate
    def test_vehicle_locations(self):
        agency_tag = 'sf-muni'
        route_tag = 'N'
        epoch_time = '1144953500233'
        test_url = nextbus.vehicle_location(agency_tag, route_tag, epoch_time)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=vehicle_locations.text,
                               content_type='application/xml')
        locations = client.nextbus.vehicle_location(agency_tag, route_tag, epoch_time)
        location = locations[0]
        self.assert_all_variables(location)

    @httpretty.activate
    def test_message_single(self):
        # Test with one arg
        agency_tag = 'sf-muni'
        route_tag = '38'
        test_url = nextbus.message_get(agency_tag, route_tag)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=message_get.text,
                               content_type='application/xml')
        routes = client.nextbus.message_get(agency_tag, route_tag)
        first_route = routes[0]
        self.assert_all_variables(first_route, skip=['agency_tag'])

    @httpretty.activate
    def test_message_multiple(self):
        # Test with mulitple args
        agency_tag = 'sf-muni'
        route_tags = ['38', '47']
        test_url = nextbus.message_get(agency_tag, route_tags)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=message_get_multi.text,
                               content_type='application/xml')
        routes = client.nextbus.message_get(agency_tag, route_tags)
        self.assertTrue(len(routes) > 1)
        first_route = routes[0]
        self.assert_all_variables(first_route, skip=['agency_tag'])

    @httpretty.activate
    def test_multi_prediction_single(self):
        # Test with one stop/route
        agency_tag = 'sf-muni'
        data = {'38' : ['13568']}
        test_url = nextbus.multiple_stop_prediction(agency_tag, data)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=multi_one.text,
                               content_type='application/xml')
        preds = client.nextbus.multiple_stop_predictions(agency_tag, data)
        first_pred = preds[0]
        self.assert_all_variables(first_pred)
        direction = first_pred.directions[0]
        self.assert_all_variables(direction)

    @httpretty.activate
    def test_multi_prediction_multiple(self):
        # Test with multiple stops on same route
        agency_tag = 'sf-muni'
        data = {'38' : ['13568', '13567']}
        test_url = nextbus.multiple_stop_prediction(agency_tag, data)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=multi_two.text,
                               content_type='application/xml')
        preds = client.nextbus.multiple_stop_predictions(agency_tag, data)
        first_pred = preds[0]
        self.assert_all_variables(first_pred)
        direction = first_pred.directions[0]
        self.assert_all_variables(direction)
