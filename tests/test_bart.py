from datetime import datetime
import httpretty

from transit import bart as client
from transit.exceptions import TransitException
from transit.modules.bart import urls
from tests import utils

from tests.data.bart import bsa
from tests.data.bart import train_count
from tests.data.bart import elevator
from tests.data.bart import error
from tests.data.bart import estimates
from tests.data.bart import estimate_all
from tests.data.bart import current_routes
from tests.data.bart import route_info
from tests.data.bart import schedule_fare
from tests.data.bart import schedule_list
from tests.data.bart import station_access
from tests.data.bart import station_info
from tests.data.bart import station_schedule

class TestBart(utils.BaseTestClient): #pylint: disable=too-many-public-methods
    def test_bart_check_datetime(self):
        client._check_datetime('03/16/1991') #pylint:disable=protected-access
        # bad types of dates
        with self.assertRaises(TransitException):
            client._check_datetime('13/01/1991') #pylint:disable=protected-access
        with self.assertRaises(TransitException):
            client._check_datetime('12/41/1991') #pylint:disable=protected-access
        with self.assertRaises(TransitException):
            client._check_datetime('12/11/91') #pylint:disable=protected-access
        # bad with random strings
        with self.assertRaises(TransitException):
            client._check_datetime('foo-bar-thing') #pylint:disable=protected-access

    @httpretty.activate
    def test_non_200_error(self):
        test_url = urls.service_advisory()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=bsa.text,
                               content_type='application/xml',
                               status=500)
        with self.assertRaises(TransitException):
            client.service_advisory()

    @httpretty.activate
    def test_error_string(self):
        test_url = urls.service_advisory()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=error.text,
                               content_type='application/xml')
        with self.assertRaises(TransitException) as e:
            client.service_advisory()
        self.assertEqual(str(e.exception), 'Invalid key:The api key was missing or invalid.')

    @httpretty.activate
    def test_bsa(self):
        test_url = urls.service_advisory()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=bsa.text,
                               content_type='application/xml')
        advisories = client.service_advisory()
        for advisory in advisories:
            self.assert_dictionary(advisory)
            self.assertTrue(isinstance(advisory['posted'], datetime))
            self.assertTrue(isinstance(advisory['expires'], datetime))

    @httpretty.activate
    def test_train_count(self):
        test_url = urls.train_count()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=train_count.text,
                               content_type='application/xml')
        count = client.train_count()
        self.assertTrue(isinstance(count, int))

    @httpretty.activate
    def test_elevator_status(self):
        test_url = urls.elevator_status()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=elevator.text,
                               content_type='application/xml')
        status = client.elevator_status()
        self.assert_dictionary(status, skip=['expires'])
        self.assertTrue(isinstance(status['posted'], datetime))

    @httpretty.activate
    def test_estimated_departures(self):
        station = 'rich'
        test_url = urls.estimated_departures(station)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=estimates.text,
                               content_type='application/xml')
        estimations = client.station_departures(station)
        self.assert_dictionary(estimations)
        for estimate in estimations:
            self.assertEqual(station.lower(), estimate['abbreviation'].lower())
            self.assertTrue(len(estimate['directions']) > 1)
            for direction in estimate['directions']:
                self.assert_dictionary(direction)
                self.assertTrue(len(direction['estimates']) > 0)
                for dir_estimate in direction['estimates']:
                    self.assert_dictionary(dir_estimate)

    @httpretty.activate
    def test_estimated_departues_with_departures(self):
        station = 'rich'
        test_url = urls.estimated_departures(station)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=estimates.text,
                               content_type='application/xml')
        estimations = client.station_departures(station, destinations=['frmt'])
        for estimate in estimations:
            self.assertEqual(station.lower(), estimate['abbreviation'].lower())
            self.assertLength(estimate['directions'], 1)
            for direction in estimate['directions']:
                self.assert_dictionary(direction)
                self.assertTrue(len(direction['estimates']) > 0)
                for dir_estimate in direction['estimates']:
                    self.assert_dictionary(dir_estimate)

    @httpretty.activate
    def test_estimated_departues_with_departures_case_sensitive(self):
        station = 'rich'
        test_url = urls.estimated_departures(station)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=estimates.text,
                               content_type='application/xml')
        estimations = client.station_departures(station, destinations=['FRMT'])
        for estimate in estimations:
            self.assertEqual(station.lower(), estimate['abbreviation'].lower())
            self.assertLength(estimate['directions'], 1)

    @httpretty.activate
    def test_url_is_lowered(self):
        station = 'RICH'
        test_url = urls.estimated_departures(station)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=estimates.text,
                               content_type='application/xml')
        ests = client.station_departures(station)
        self.assertEqual(len(ests), 1)

    @httpretty.activate
    def test_multiple_stations(self):
        station = 'all'
        test_url = urls.estimated_departures(station)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=estimate_all.text,
                               content_type='application/xml')
        estimations = client.station_departures(station)
        for estimate in estimations:
            for direction in estimate['directions']:
                self.assert_dictionary(direction)
                self.assertTrue(len(direction['estimates']) > 0)
                for dir_estimate in direction['estimates']:
                    self.assert_dictionary(dir_estimate)

    @httpretty.activate
    def test_multiple_stations_custom(self):
        station = 'all'
        test_url = urls.estimated_departures(station)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=estimate_all.text,
                               content_type='application/xml')
        station_data = {
            # test station is lowered as well
            'mont' : ['dubl', 'Pitt'],
            'bayf' : [],
            'HAYW' : ['DALY'],
        }
        ests = client.station_multiple_departures(station_data)
        for est in ests:
            if est['abbreviation'].lower() == 'mont':
                self.assertEqual(len(est['directions']), 2)
            elif est['abbreviation'].lower() == 'bayf':
                self.assertTrue(len(est['directions']) > 0)
            elif est['abbreviation'].lower() == 'hayw':
                self.assertTrue(len(est['directions']) > 0)
            self.assert_dictionary(est)

    @httpretty.activate
    def test_route_list(self):
        test_url = urls.route_list()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=current_routes.text,
                               content_type='application/xml')
        routes = client.route_list()
        self.assert_dictionary(routes)

    @httpretty.activate
    def test_route_info(self):
        route_number = 4
        test_url = urls.route_info(route_number)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=route_info.text,
                               content_type='application/xml')
        route = client.route_info(route_number)
        self.assert_dictionary(route)

    def test_station_list(self):
        stations = client.station_list()
        self.assert_dictionary(stations)

    @httpretty.activate
    def test_station_info(self):
        station_abbr = 'rich'
        test_url = urls.station_info(station_abbr)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=station_info.text,
                               content_type='application/xml')
        station = client.station_info(station_abbr)
        self.assert_dictionary(station)
        self.assertTrue(len(station['north_routes']) > 0)
        self.assertTrue(len(station['south_routes']) > 0)
        self.assertTrue(len(station['south_platforms']) > 0)
        self.assertTrue(len(station['north_platforms']) > 0)

    @httpretty.activate
    def test_station_access(self):
        station_abbr = '12th'
        test_url = urls.station_access(station_abbr)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=station_access.text,
                               content_type='application/xml')
        station = client.station_access(station_abbr)
        self.assert_dictionary(station)

    @httpretty.activate
    def test_station_schedule(self):
        station_abbr = '12th'
        test_url = urls.station_schedule(station_abbr)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=station_schedule.text,
                               content_type='application/xml')
        station = client.station_schedule(station_abbr)
        self.assert_dictionary(station)
        self.assertTrue(len(station['schedule_times']) > 0)
        for times in station['schedule_times']:
            self.assert_dictionary(times)
            self.assertTrue(isinstance(times['origin_time'], datetime))
            self.assertTrue(isinstance(times['destination_time'], datetime))

    @httpretty.activate
    def test_schedule(self):
        test_url = urls.schedule_list()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=schedule_list.text,
                               content_type='application/xml')
        schedules = client.schedule_list()
        self.assert_dictionary(schedules)
        for sched in schedules:
            self.assert_dictionary(sched)

    @httpretty.activate
    def test_schedule_fare(self):
        origin = '12th'
        dest = 'embr'
        test_url = urls.schedule_fare(origin, dest)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=schedule_fare.text,
                               content_type='application/xml')
        fare = client.schedule_fare(origin, dest)
        self.assert_dictionary(fare)
