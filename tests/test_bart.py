from datetime import datetime
import unittest

from jsonschema import ValidationError
import httpretty

from transit import bart as client
from transit.exceptions import TransitException
from transit.modules.bart import urls

from tests.data.bart import bsa
from tests.data.bart import train_count
from tests.data.bart import departure_with_platform
from tests.data.bart import departure_with_direction
from tests.data.bart import elevator
from tests.data.bart import error
from tests.data.bart import estimates
from tests.data.bart import estimate_all
from tests.data.bart import route_list
from tests.data.bart import route_info
from tests.data.bart import schedule_fare
from tests.data.bart import schedule_list
from tests.data.bart import station_access
from tests.data.bart import station_info
from tests.data.bart import station_schedule

class TestBart(unittest.TestCase): #pylint: disable=too-many-public-methods

    @httpretty.activate
    def test_non_200_error(self):
        test_url = urls.service_advisory()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=bsa.text,
                               content_type='application/xml',
                               status=500)
        with self.assertRaises(TransitException) as sa_error:
            client.service_advisory()
        self.assertTrue("does not return 200" in str(sa_error.exception))

    @httpretty.activate
    def test_error_string(self):
        test_url = urls.service_advisory()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=error.text,
                               content_type='application/xml')
        with self.assertRaises(TransitException) as e:
            client.service_advisory()
        self.assertEqual(str(e.exception), "b'Invalid key':b'The api key was missing or invalid.'")

    @httpretty.activate
    def test_specify_api_key(self):
        test_url = urls.service_advisory(key='foo')
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=bsa.text,
                               content_type='application/xml')
        advisories = client.service_advisory(api_key='foo')
        for advisory in advisories:
            self.assertTrue(isinstance(advisory['posted'], datetime))
            self.assertTrue(isinstance(advisory['expires'], datetime))
            self.assertTrue(len(advisory['description']) > 0)
            self.assertEqual(advisory['station'], 'bart')
            self.assertTrue(isinstance(advisory['id'], int))
            self.assertEqual(advisory['type'], 'delay')

    @httpretty.activate
    def test_bsa(self):
        test_url = urls.service_advisory()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=bsa.text,
                               content_type='application/xml')
        advisories = client.service_advisory()
        for advisory in advisories:
            self.assertTrue(isinstance(advisory['posted'], datetime))
            self.assertTrue(isinstance(advisory['expires'], datetime))
            self.assertTrue(len(advisory['description']) > 0)
            self.assertEqual(advisory['station'], 'bart')
            self.assertTrue(isinstance(advisory['id'], int))
            self.assertEqual(advisory['type'], 'delay')

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
        self.assertTrue(isinstance(status['posted'], datetime))
        self.assertEqual(status['type'], 'elevator')
        self.assertEqual(status['station'], 'bart')
        self.assertEqual(status['expires'], None)
        self.assertTrue(len(status['description']) > 0)

    @httpretty.activate
    def test_estimated_departures(self):
        station = 'rich'
        test_url = urls.estimated_departures(station)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=estimates.text,
                               content_type='application/xml')
        estimations = client.station_departures(station)
        for estimate in estimations:
            self.assertEqual(station, estimate['abbreviation'])
            self.assertEqual('Richmond', estimate['name'])
            self.assertEqual(len(estimate['directions']), 2)
            for direct in estimate['directions']:
                self.assertEqual(direct['abbreviation'],
                                 direct['abbreviation'].lower())
                self.assertTrue(len(direct['estimates']) > 0)
                for dir_estimate in direct['estimates']:
                    self.assertEqual(dir_estimate['direction'], 'south')
                    self.assertEqual(dir_estimate['color'],
                                     dir_estimate['color'].lower())
                    self.assertTrue(isinstance(dir_estimate['length'], int))
                    self.assertTrue(isinstance(dir_estimate['platform'], int))
                    self.assertTrue(isinstance(dir_estimate['minutes'], int))
                    self.assertFalse(dir_estimate['bike_flag'])

    @httpretty.activate
    def test_estimated_departures_with_platform(self):
        station = 'rich'
        test_url = urls.estimated_departures(station, platform=2)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=departure_with_platform.text,
                               content_type='application/xml')
        estimations = client.station_departures(station, platform=2)
        for estimate in estimations:
            for direct in estimate['directions']:
                for dir_est in direct['estimates']:
                    self.assertEqual(dir_est['platform'], 2)

    @httpretty.activate
    def test_estimated_departures_with_direction(self):
        station = 'rich'
        test_url = urls.estimated_departures(station, direction="s")
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=departure_with_direction.text,
                               content_type='application/xml')
        estimations = client.station_departures(station, direction="s")
        for estimate in estimations:
            for direct in estimate['directions']:
                for dir_est in direct['estimates']:
                    self.assertEqual(dir_est['direction'], 'south')

    @httpretty.activate
    def test_estimated_departures_with_departures(self):
        station = 'rich'
        test_url = urls.estimated_departures(station)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=estimates.text,
                               content_type='application/xml')
        estimations = client.station_departures(station, destinations=['frmt'])
        for estimate in estimations:
            self.assertEqual(estimate['abbreviation'], 'rich')
            self.assertEqual(estimate['name'], 'Richmond')
            self.assertEqual(len(estimate['directions']), 1)

    @httpretty.activate
    def test_multiple_stations(self):
        station = 'all'
        test_url = urls.estimated_departures(station)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=estimate_all.text,
                               content_type='application/xml')
        estimations = client.station_departures(station)
        # All stations have more data, but this is stripped
        # .. to speed up testing a little
        self.assertEqual(len(estimations), 5)

    def test_multiple_stations_validation_error(self):
        station_data = {
            'mont' : 2,
        }
        with self.assertRaises(ValidationError) as val_error:
            client.station_multiple_departures(station_data)
        self.assertTrue("2 is not of type 'array'" in str(val_error.exception))

    @httpretty.activate
    def test_multiple_stations_custom(self):
        station = 'all'
        test_url = urls.estimated_departures(station)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=estimate_all.text,
                               content_type='application/xml')
        station_data = {
            'mont' : ['dubl', 'pitt'],
            'bayf' : [],
            'hayw' : ['daly'],
        }
        ests = client.station_multiple_departures(station_data)
        self.assertEqual(len(ests), 3)
        for est in ests:
            if est['abbreviation'].lower() == 'mont':
                self.assertEqual(len(est['directions']), 2)
            elif est['abbreviation'].lower() == 'bayf':
                self.assertEqual(len(est['directions']), 4)
            elif est['abbreviation'].lower() == 'hayw':
                self.assertEqual(len(est['directions']), 1)

    @httpretty.activate
    def test_route_list(self):
        test_url = urls.route_list()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=route_list.text,
                               content_type='application/xml')
        route_data = client.route_list()
        self.assertEqual(route_data['schedule_number'], 35)
        for route in route_data['routes']:
            self.assertTrue(isinstance(route['number'], int))
            self.assertEqual(route['abbreviation'],
                             route['abbreviation'].lower())

    @httpretty.activate
    def test_route_list_with_schedule(self):
        # This is mostly here to check that url scheme works
        # correctly
        test_url = urls.route_list(schedule=35)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=route_list.text,
                               content_type='application/xml')
        route_data = client.route_list(schedule=35)
        self.assertTrue('schedule_number' in route_data.keys())

    @httpretty.activate
    def test_route_list_with_date(self):
        # This is mostly here to check that url scheme works
        # correctly
        test_url = urls.route_list(date="03/17/2017")
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=route_list.text,
                               content_type='application/xml')
        route_data = client.route_list(date="03/17/2017")
        self.assertTrue('schedule_number' in route_data.keys())

    @httpretty.activate
    def test_route_info(self):
        route_number = 4
        test_url = urls.route_info(route_number)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=route_info.text,
                               content_type='application/xml')
        route = client.route_info(route_number)
        self.assertEqual(route['origin'],
                         route['origin'].lower())
        self.assertEqual(route['destination'],
                         route['destination'].lower())
        self.assertEqual(route['abbreviation'],
                         route['abbreviation'].lower())
        for station in route['stations']:
            self.assertEqual(station, station.lower())
        self.assertTrue(route['holidays'])
        self.assertTrue(isinstance(route['number'], int))
        self.assertTrue(isinstance(route['number_of_stations'], int))

    @httpretty.activate
    def test_route_info_with_schedule(self): #pylint:disable=no-self-use
        # This is mostly here to check that url scheme works
        # correctly
        route_number = 4
        test_url = urls.route_info(route_number, schedule=35)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=route_info.text,
                               content_type='application/xml')
        client.route_info(route_number, schedule=35)

    @httpretty.activate
    def test_route_info_with_date(self): #pylint:disable=no-self-use
        # This is mostly here to check that url scheme works
        # correctly
        route_number = 4
        test_url = urls.route_info(route_number, date="03/17/2017")
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=route_info.text,
                               content_type='application/xml')
        client.route_info(route_number, date="03/17/2017")

    def test_station_list(self):
        stations = client.station_list()
        for key in stations:
            self.assertEqual(key.lower(), key)

    @httpretty.activate
    def test_station_info(self):
        station_abbr = 'rich'
        test_url = urls.station_info(station_abbr)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=station_info.text,
                               content_type='application/xml')
        station = client.station_info(station_abbr)
        self.assertTrue(len(station['north_routes']) > 0)
        self.assertTrue(len(station['south_routes']) > 0)
        self.assertTrue(len(station['south_platforms']) > 0)
        self.assertTrue(len(station['north_platforms']) > 0)
        self.assertEqual(station['abbreviation'].lower(),
                         station['abbreviation'])
        self.assertTrue(isinstance(station['zipcode'], int))
        self.assertTrue(isinstance(station['gtfs_latitude'], float))
        self.assertTrue(isinstance(station['gtfs_longitude'], float))

    @httpretty.activate
    def test_station_access(self):
        station_abbr = '12th'
        test_url = urls.station_access(station_abbr)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=station_access.text,
                               content_type='application/xml')
        station = client.station_access(station_abbr)
        self.assertFalse(station['locker_flag'])
        self.assertFalse(station['bike_flag'])
        self.assertFalse(station['parking_flag'])
        self.assertEqual(station['abbreviation'],
                         station['abbreviation'].lower())

    @httpretty.activate
    def test_station_schedule(self):
        station_abbr = '12th'
        test_url = urls.station_schedule(station_abbr)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=station_schedule.text,
                               content_type='application/xml')
        station = client.station_schedule(station_abbr)
        self.assertEqual(station['abbreviation'],
                         station['abbreviation'].lower())
        for item in station['schedule_times']:
            self.assertEqual(item['head_station'],
                             item['head_station'].lower())
            self.assertTrue(isinstance(item['line'], int))
            self.assertTrue(isinstance(item['train_index'], int))
            self.assertTrue(isinstance(item['bike_flag'], bool))
            self.assertTrue(isinstance(item['origin_time'], datetime))
            self.assertTrue(isinstance(item['destination_time'], datetime))

    @httpretty.activate
    def test_station_schedule_with_date(self): #pylint:disable=no-self-use
        # Mostly here to test url creation
        station_abbr = '12th'
        test_url = urls.station_schedule(station_abbr, date="03/17/2017")
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=station_schedule.text,
                               content_type='application/xml')
        client.station_schedule(station_abbr, date="03/17/2017")

    @httpretty.activate
    def test_schedule(self):
        test_url = urls.schedule_list()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=schedule_list.text,
                               content_type='application/xml')
        schedules = client.schedule_list()
        for sched in schedules:
            self.assertTrue(isinstance(sched['id'], int))
            self.assertTrue(isinstance(sched['effective_date'], datetime))

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
        self.assertEqual(fare['origin'],
                         fare['origin'].lower())
        self.assertEqual(fare['destination'],
                         fare['destination'].lower())
        self.assertTrue(isinstance(fare['fare'], float))
        self.assertTrue(isinstance(fare['discount'], float))
        self.assertTrue(isinstance(fare['clipper'], float))
        self.assertTrue(isinstance(fare['schedule_number'], int))

    @httpretty.activate
    def test_schedule_fare_with_schedule(self): #pylint:disable=no-self-use
        # Mostly here to test url
        origin = '12th'
        dest = 'embr'
        test_url = urls.schedule_fare(origin, dest, schedule=35)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=schedule_fare.text,
                               content_type='application/xml')
        client.schedule_fare(origin, dest, schedule=35)

    @httpretty.activate
    def test_schedule_fare_with_date(self): #pylint:disable=no-self-use
        # Mostly here to test url
        origin = '12th'
        dest = 'embr'
        test_url = urls.schedule_fare(origin, dest, date="03/17/2017")
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=schedule_fare.text,
                               content_type='application/xml')
        client.schedule_fare(origin, dest, date="03/17/2017")
