import json

import httpretty

from transit import actransit
from transit.exceptions import TransitException
from transit.modules.actransit import urls

from tests.data.actransit import notices
from tests.data.actransit import route_directions
from tests.data.actransit import route_list
from tests.data.actransit import route_stops
from tests.data.actransit import route_trips
from tests.data.actransit import stop_predictions
from tests.utils import TestRunnerHelper


FAKE_TOKEN = 'abc1234'

class TestActransit(TestRunnerHelper):
    @httpretty.activate
    def test_route_list(self):
        test_url = urls.route_list(FAKE_TOKEN)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=json.dumps(route_list.DATA),
                               content_type='application/json')
        route_data = actransit.route_list(FAKE_TOKEN)
        for item in route_data:
            self.assertNotEqual(item['Name'], None)
            self.assertNotEqual(item['RouteId'], None)
            self.assertNotEqual(item['Description'], None)

    @httpretty.activate
    def test_route_directions(self):
        test_url = urls.route_directions(FAKE_TOKEN, '51A')
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=json.dumps(route_directions.DATA),
                               content_type='application/json')
        route_dirs = actransit.route_directions(FAKE_TOKEN, '51A')
        for direct in route_dirs:
            self.assertNotEqual(direct, None)

    @httpretty.activate
    def test_route_trips(self):
        test_url = urls.route_trips(FAKE_TOKEN, '51A', 'Southbound', '0')
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=json.dumps(route_trips.DATA),
                               content_type='application/json')
        trips = actransit.route_trips(FAKE_TOKEN, '51A', 'Southbound')
        for trip in trips:
            self.assertNotEqual(trip['TripId'], None)
            self.assertNotEqual(trip['StartTime'], None)

    def test_route_trips_bad_schedule(self):
        with self.assertRaises(TransitException) as error:
            actransit.route_trips(FAKE_TOKEN, '51A', 'Southbound', schedule_type='foo')
        self.check_error_message(error, "Invalid schedule type:foo")

    @httpretty.activate
    def test_route_stops(self):
        test_url = urls.route_stops(FAKE_TOKEN, '51A', '6783494')
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=json.dumps(route_stops.DATA),
                               content_type='application/json')
        stops = actransit.route_stops(FAKE_TOKEN, '51A', '6783494')
        for stop in stops:
            self.assertNotEqual(stop['Name'], None)
            self.assertNotEqual(stop['StopId'], None)
            self.assertNotEqual(stop['Longitude'], None)
            self.assertNotEqual(stop['Latitude'], None)

    @httpretty.activate
    def test_stop_predictions(self):
        test_url = urls.stop_predictions(FAKE_TOKEN, '51303')
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=json.dumps(stop_predictions.DATA),
                               content_type='application/json')
        predictions = actransit.stop_predictions(FAKE_TOKEN, '51303')
        for pred in predictions:
            self.assertNotEqual(pred['RouteName'], None)
            self.assertNotEqual(pred['PredictedDeparture'], None)
            self.assertNotEqual(pred['PredictionDateTime'], None)
            self.assertNotEqual(pred['PredictedDelayInSeconds'], None)
            self.assertNotEqual(pred['VehicleId'], None)
            self.assertNotEqual(pred['TripId'], None)

    @httpretty.activate
    def test_service_notices(self):
        test_url = urls.service_notices(FAKE_TOKEN)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=json.dumps(notices.DATA),
                               content_type='application/json')
        notes = actransit.service_notices(FAKE_TOKEN)
        for note in notes:
            self.assertNotEqual(note['Url'], None)
            self.assertNotEqual(note['Title'], None)
            self.assertNotEqual(note['NoticeText'], None)
            self.assertNotEqual(note['PostDate'], None)
            self.assertNotEqual(note['ImpactedRoutes'], None)
            for route in note['ImpactedRoutes']:
                self.assertNotEqual(route, None)
