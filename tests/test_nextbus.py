from datetime import datetime
import unittest

from jsonschema import ValidationError
import httpretty

from transit import nextbus as client
from transit.exceptions import TransitException
from transit.modules.nextbus import urls

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

class TestNextbus(unittest.TestCase):
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
        for agency in agencies:
            self.assertEqual(agency['tag'],
                             agency['tag'].lower())
            self.assertNotEqual(agency['title'],
                                agency['title'].lower())
            self.assertNotEqual(agency['region'],
                                agency['region'].lower())

    @httpretty.activate
    def test_route_list(self):
        agency_tag = 'sf-muni'
        test_url = urls.route_list(agency_tag)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=route_list.text,
                               content_type='application/xml')
        routes = client.route_list(agency_tag)
        for route in routes:
            self.assertTrue(isinstance(route['title'], str))
            self.assertTrue(isinstance(route['tag'], str))

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
        self.assertTrue(isinstance(route['tag'], str))
        self.assertTrue(isinstance(route['title'], str))
        self.assertTrue(isinstance(route['opposite_color'], str))
        self.assertTrue(isinstance(route['color'], str))
        self.assertTrue(isinstance(route['longitude_max'], float))
        self.assertTrue(isinstance(route['longitude_min'], float))
        self.assertTrue(isinstance(route['longitude_max'], float))
        self.assertTrue(isinstance(route['longitude_min'], float))

        for path in route['paths']:
            for point in path:
                self.assertTrue(isinstance(point['longitude'], float))
                self.assertTrue(isinstance(point['latitude'], float))

        for stop in route['stops']:
            self.assertTrue(isinstance(stop['title'], str))
            self.assertTrue(isinstance(stop['stop_tag'], str))
            self.assertTrue(isinstance(stop['stop_id'], str))
            self.assertTrue(isinstance(stop['longitude'], float))
            self.assertTrue(isinstance(stop['latitude'], float))

        for direction in route['directions']:
            self.assertTrue(isinstance(direction['title'], str))
            self.assertTrue(isinstance(direction['name'], str))
            self.assertTrue(isinstance(direction['tag'], str))
            self.assertTrue(isinstance(direction['use_for_ui'], bool))
            for stop_tag in direction['stop_tags']:
                self.assertTrue(isinstance(stop_tag, str))

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
            self.assertTrue(isinstance(prediction['route_tag'], str))
            self.assertTrue(isinstance(prediction['agency_title'], str))
            self.assertTrue(isinstance(prediction['route_title'], str))
            self.assertTrue(isinstance(prediction['stop_title'], str))
            for message in prediction['messages']:
                self.assertTrue(isinstance(message, str))
            for direction in prediction['directions']:
                self.assertTrue(isinstance(direction['title'], str))
                for pred in direction['predictions']:
                    self.assertTrue(isinstance(pred['trip_tag'], str))
                    self.assertTrue(isinstance(pred['dir_tag'], str))
                    self.assertTrue(isinstance(pred['vehicle'], str))
                    self.assertTrue(isinstance(pred['block'], str))
                    self.assertTrue(isinstance(pred['affected_by_layover'], bool))
                    self.assertTrue(isinstance(pred['is_departure'], bool))
                    self.assertTrue(isinstance(pred['epoch_time'], int))
                    self.assertTrue(isinstance(pred['minutes'], int))
                    self.assertTrue(isinstance(pred['seconds'], int))

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
        # Everything else caught in test above

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
        # Everything else caught in test above

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
        # Everything else caught in test above

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
            self.assertTrue(isinstance(schedule['title'], str))
            self.assertTrue(isinstance(schedule['tag'], str))
            self.assertTrue(isinstance(schedule['service_class'], str))
            self.assertTrue(isinstance(schedule['schedule_class'], str))
            self.assertTrue(isinstance(schedule['direction'], str))
            for block in schedule['blocks']:
                self.assertTrue(isinstance(block['block_id'], str))
                for stop in block['stop_schedules']:
                    self.assertTrue(isinstance(stop['stop_tag'], str))
                    self.assertTrue(isinstance(stop['title'], str))
                    self.assertTrue(isinstance(stop['epoch_time'], int))
                    if stop['time']:
                        self.assertTrue(isinstance(stop['time'], datetime))

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
            self.assertTrue(isinstance(location['seconds_since_last_report'], int))
            self.assertTrue(isinstance(location['speed_km_hr'], int))
            self.assertTrue(isinstance(location['longitude'], float))
            self.assertTrue(isinstance(location['latitude'], float))
            self.assertTrue(isinstance(location['predictable'], bool))
            self.assertTrue(isinstance(location['route_tag'], str))
            self.assertTrue(isinstance(location['heading'], str))
            self.assertTrue(isinstance(location['vehicle_id'], str))

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
            self.assertTrue(isinstance(route['tag'], str))
            for message in route['messages']:
                self.assertTrue(isinstance(message['message_id'], str))
                self.assertTrue(isinstance(message['priority'], str))
                for text in message['text']:
                    self.assertTrue(isinstance(text, str))

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
        # Assume test above will catch errors

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
        # Normal predictions will catch all cases

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
        # Normal predictions will catch all cases
