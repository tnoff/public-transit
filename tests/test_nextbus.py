from datetime import datetime
from jsonschema import ValidationError
import httpretty

from transit import nextbus as client
from transit.exceptions import TransitException
from transit.modules.nextbus import urls

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

class TestNextbus(utils.BaseTestClient):
    @httpretty.activate
    def test_fails_error(self):
        # Check that failures catch nicely
        # Failure xml format in nextbus docs
        test_url = urls.agency_list()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=error.text,
                               content_type='application/xml')
        with self.assertRaises(TransitException) as e:
            client.agency_list()
        self.assertEqual(str(e.exception), 'agency parameter "a" must be specified in query string')

    @httpretty.activate
    def test_fails_invalid_code(self):
        test_url = urls.agency_list()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=agency_list.text,
                               content_type='application/xml',
                               status=500)
        with self.assertRaises(TransitException) as e:
            client.agency_list()
        self.assertEqual(str(e.exception), 'Non-200 status code returned')

    @httpretty.activate
    def test_agency_list(self):
        test_url = urls.agency_list()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=agency_list.text,
                               content_type='application/xml')
        agencies = client.agency_list()
        self.assert_dictionary(agencies)
        for agency in agencies:
            self.assert_dictionary(agency)

    @httpretty.activate
    def test_route_list(self):
        agency_tag = 'sf-muni'
        test_url = urls.route_list(agency_tag)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=route_list.text,
                               content_type='application/xml')
        routes = client.route_list(agency_tag)
        self.assert_dictionary(routes)
        for route in routes:
            self.assert_dictionary(route)

    @httpretty.activate
    def test_route_show(self):
        agency_tag = 'actransit'
        route_tag = '801'
        test_url = urls.route_show(agency_tag, route_tag)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=route_show.text,
                               content_type='application/xml')
        route = client.route_show(agency_tag, route_tag)
        self.assert_dictionary(route)
        for stop in route['stops']:
            self.assert_dictionary(stop, skip=['short_title'])
        for direction in route['directions']:
            self.assert_dictionary(direction)
        for path in route['paths']:
            self.assert_dictionary(path)

    @httpretty.activate
    def test_stop_prediction_no_route(self):
        agency_tag = 'actransit'
        stop_id = '51303'
        test_url = urls.stop_prediction(agency_tag, stop_id)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=stop_predictions.text,
                               content_type='application/xml')
        predictions = client.stop_prediction(agency_tag, stop_id)
        for prediction in predictions:
            self.assert_dictionary(prediction)
            for direction in prediction['directions']:
                self.assert_dictionary(direction)
                for pred in direction['predictions']:
                    self.assert_dictionary(pred)

    @httpretty.activate
    def test_stop_prediction_with_route(self):
        agency_tag = 'actransit'
        stop_id = '51303'
        route_tag = '22'
        test_url = urls.stop_prediction(agency_tag, stop_id,
                                        route_tags=route_tag)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=stop_predictions_route.text,
                               content_type='application/xml')
        predictions = client.stop_prediction(agency_tag, stop_id,
                                             route_tags=[route_tag])
        self.assertTrue(len(predictions) > 0)
        for prediction in predictions:
            self.assert_dictionary(prediction)
            for direction in prediction['directions']:
                self.assert_dictionary(direction)
                for pred in direction['predictions']:
                    self.assert_dictionary(pred)

    @httpretty.activate
    def test_stop_prediction_with_route_as_list(self):
        agency_tag = 'actransit'
        stop_id = '51303'
        route_tag = ['22']
        test_url = urls.stop_prediction(agency_tag, stop_id,
                                        route_tags=route_tag)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=stop_predictions_route.text,
                               content_type='application/xml')
        predictions = client.stop_prediction(agency_tag, stop_id,
                                             route_tags=route_tag)
        self.assertTrue(len(predictions) > 0)
        for prediction in predictions:
            self.assert_dictionary(prediction)
            for direction in prediction['directions']:
                self.assert_dictionary(direction)
                for pred in direction['predictions']:
                    self.assert_dictionary(pred)

    @httpretty.activate
    def test_stop_prediction_with_route_multi(self):
        agency_tag = 'actransit'
        stop_id = '51303'
        route_tags = ['22', '99']
        test_url = urls.stop_prediction(agency_tag, stop_id,
                                        route_tags=route_tags)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=stop_predictions.text,
                               content_type='application/xml')
        predictions = client.stop_prediction(agency_tag, stop_id,
                                             route_tags=route_tags)
        self.assertTrue(len(predictions) > 0)
        for prediction in predictions:
            self.assert_dictionary(prediction)
            for direction in prediction['directions']:
                self.assert_dictionary(direction)
                for pred in direction['predictions']:
                    self.assert_dictionary(pred)

    @httpretty.activate
    def test_schedule(self):
        agency_tag = 'actransit'
        route_tag = '22'
        test_url = urls.schedule_get(agency_tag, route_tag)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=schedule_get.text,
                               content_type='application/xml')
        schedules = client.schedule_get(agency_tag, route_tag)
        for schedule in schedules:
            self.assert_dictionary(schedule)
            for block in schedule['blocks']:
                self.assert_dictionary(block)
                for stop_schedule in block['stop_schedules']:
                    self.assert_dictionary(stop_schedule, skip=['time'])
                    time = stop_schedule['time']
                    if time is not None:
                        self.assertTrue(isinstance(time, datetime))

    @httpretty.activate
    def test_vehicle_locations(self):
        agency_tag = 'sf-muni'
        route_tag = 'N'
        epoch_time = 1144953500233
        test_url = urls.vehicle_location(agency_tag, route_tag, epoch_time)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=vehicle_locations.text,
                               content_type='application/xml')
        locations = client.vehicle_location(agency_tag, route_tag, epoch_time)
        for location in locations:
            self.assert_dictionary(location)

    @httpretty.activate
    def test_message_single(self):
        # Test with one arg
        agency_tag = 'sf-muni'
        route_tag = '38'
        test_url = urls.message_get(agency_tag, route_tag)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=message_get.text,
                               content_type='application/xml')
        routes = client.route_messages(agency_tag, [route_tag])
        for route in routes:
            self.assert_dictionary(route, skip=['agency_tag'])

    @httpretty.activate
    def test_message_multiple(self):
        # Test with mulitple args
        agency_tag = 'sf-muni'
        route_tags = ['38', '47']
        test_url = urls.message_get(agency_tag, route_tags)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=message_get_multi.text,
                               content_type='application/xml')
        routes = client.route_messages(agency_tag, route_tags)
        self.assertTrue(len(routes) > 1)
        for route in routes:
            self.assert_dictionary(route, skip=['agency_tag'])

    def test_multi_prediction_validation_error(self):
        data = {
            'foo12' : 2,
        }
        with self.assertRaises(ValidationError) as val_error:
            client.stop_multiple_predictions('sf-muni', data)
        self.assertTrue("2 is not of type 'array'" in str(val_error.exception))

        # empty list should fail
        data = {
            'foo12' : [],
        }
        with self.assertRaises(ValidationError) as val_error:
            client.stop_multiple_predictions('sf-muni', data)
        self.assertTrue("[] is too short" in str(val_error.exception))

    @httpretty.activate
    def test_multi_prediction_single_route(self):
        # Test with one stop/route
        agency_tag = 'sf-muni'
        data = {'13568' : ['38']}
        test_url = urls.multiple_stop_prediction(agency_tag, data)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=multi_one.text,
                               content_type='application/xml')
        preds = client.stop_multiple_predictions(agency_tag, data)
        self.assertTrue(len(preds) > 0)
        for prediction in preds:
            self.assert_dictionary(prediction)
            for direction in prediction['directions']:
                self.assert_dictionary(direction)

    @httpretty.activate
    def test_multi_prediction_multiple_route(self):
        # Test with multiple stops on same route
        agency_tag = 'sf-muni'
        data = {'13568' : ['38',], '13567' : ['38']}
        test_url = urls.multiple_stop_prediction(agency_tag, data)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=multi_two.text,
                               content_type='application/xml')
        preds = client.stop_multiple_predictions(agency_tag, data)
        self.assertTrue(len(preds) > 1)
        for prediction in preds:
            self.assert_dictionary(prediction)
            for direction in prediction['directions']:
                self.assert_dictionary(direction)
