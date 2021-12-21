import json

import httpretty
import pytest

from transit.modules.actransit import client
from transit.exceptions import TransitException
from transit.modules.actransit import urls

from tests.data.actransit.notices import DATA as notices
from tests.data.actransit.route_directions import DATA as route_directions
from tests.data.actransit.route_list import DATA as route_list
from tests.data.actransit.route_stops import DATA as route_stops
from tests.data.actransit.route_trips import DATA as route_trips
from tests.data.actransit.stop_predictions import DATA as stop_predictions


FAKE_TOKEN = 'abc1234'

def test_route_list(requests_mock):
    requests_mock.get(urls.route_list(FAKE_TOKEN), json=route_list)
    route_data = client.route_list(FAKE_TOKEN)
    for item in route_data:
        assert item['Name'] != None
        assert item['RouteId'] !=  None
        assert item['Description'] != None

def test_route_directions(requests_mock):
    requests_mock.get(urls.route_directions(FAKE_TOKEN, '51A'), json=route_directions)
    route_dirs = client.route_directions(FAKE_TOKEN, '51A')
    for direct in route_dirs:
        assert direct != None

def test_route_trips(requests_mock):
    requests_mock.get(urls.route_trips(FAKE_TOKEN, '51A', 'Southbound', '0'),
                      json=route_trips)
    trips = client.route_trips(FAKE_TOKEN, '51A', 'Southbound')
    for trip in trips:
        assert trip['TripId'] != None
        assert trip['StartTime'] != None

def test_route_trips_bad_schedule(requests_mock):
    with pytest.raises(TransitException) as e:
        client.route_trips(FAKE_TOKEN, '51A', 'Southbound', schedule_type='foo')
    assert 'Invalid schedule type: "foo"' == str(e.value)

def test_route_stops(requests_mock):
    requests_mock.get(urls.route_stops(FAKE_TOKEN, '51A', '6783494'),
                      json=route_stops)
    stops = client.route_stops(FAKE_TOKEN, '51A', '6783494')
    for stop in stops:
        stop['Name'] != None
        stop['StopId'] != None
        stop['Longitude'] != None
        stop['Latitude'] != None

def test_stop_predictions(requests_mock):
    requests_mock.get(urls.stop_predictions(FAKE_TOKEN, ['55511'], None),
                      json=stop_predictions)
    predictions = client.stop_predictions(FAKE_TOKEN, '55511')
    for pred in predictions['bustime-response']['prd']:
        pred['tmstmp'] != None
        pred['stpnm'] != None
        pred['rtdir'] != None
        pred['prdtm'] != None

def test_service_notices(requests_mock):
    requests_mock.get(urls.service_notices(FAKE_TOKEN),
                      json=notices)
    notes = client.service_notices(FAKE_TOKEN)
    for note in notes:
        note['Url'] != None
        note['Title'] != None
        note['NoticeText'] != None
        note['PostDate'] != None
        note['ImpactedRoutes'] != None
        for route in note['ImpactedRoutes']:
            route != None

"""

class TestActransit(TestRunnerHelper):

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
"""