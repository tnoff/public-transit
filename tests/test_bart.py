from datetime import datetime
import httpretty

from transit import bart as client
from transit.exceptions import TransitException
from transit.modules.bart import urls
from tests import utils

from tests.data.bart import bsa
from tests.data.bart import bsa_no_delay
from tests.data.bart import train_count
from tests.data.bart import elevator
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
    def test_bsa(self):
        test_url = urls.service_advisory()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=bsa.text,
                               content_type='application/xml')
        advisories = client.service_advisory()
        # should only be one advisory in data anyway
        adv = advisories[0]
        self.assert_dictionary(adv)
        self.assertTrue(isinstance(adv['expires'], datetime))

    @httpretty.activate
    def test_bsa_delay(self):
        test_url = urls.service_advisory()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=bsa_no_delay.text,
                               content_type='application/xml')
        advisories = client.service_advisory()
        # should only be one advisory in data anyway
        adv = advisories[0]
        self.assert_dictionary(adv, skip=['station', 'type', 'posted',
                                          'expires', 'id'])
        # find first description, make sure its a string
        desc = adv['description']
        self.assertTrue(isinstance(desc, basestring))

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
        desc = status['description']
        self.assertTrue(isinstance(desc, basestring))

    @httpretty.activate
    def test_estimated_departures(self):
        station = 'rich'
        test_url = urls.estimated_departures(station)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=estimates.text,
                               content_type='application/xml')
        ests = client.station_departures(station)
        est = ests[0]
        self.assert_dictionary(est)
        self.assertEqual(station.lower(), est['abbreviation'].lower())
        self.assertTrue(len(est['directions']) > 1)
        direction = est['directions'][0]
        self.assert_dictionary(direction)
        self.assertTrue(len(direction['estimates']) > 0)
        direction_estimate = direction['estimates'][0]
        self.assert_dictionary(direction_estimate)

        # test with destinations
        ests = client.station_departures(station,
                                         destinations=['frmt'])
        est = ests[0]
        self.assertEqual(len(est['directions']), 1)

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
        ests = client.station_departures(station)
        self.assertTrue(len(ests) > 0)
        for est in ests:
            self.assert_dictionary(est)
            direction = est['directions'][0]
            self.assert_dictionary(direction)
            self.assertTrue(len(direction['estimates']) > 0)
            direction_estimate = direction['estimates'][0]
            self.assert_dictionary(direction_estimate)

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
        }
        ests = client.station_multiple_departures(station_data)
        for est in ests:
            if est['abbreviation'].lower() == 'mont':
                self.assertEqual(len(est['directions']), 2)
            elif est['abbreviation'].lower() == 'bayf':
                self.assertTrue(len(est['directions']) > 0)
            self.assert_dictionary(est)
            direction = est['directions'][0]
            self.assert_dictionary(direction)
            self.assertTrue(len(direction['estimates']) > 0)
            direction_estimate = direction['estimates'][0]
            self.assert_dictionary(direction_estimate)

    @httpretty.activate
    def test_route_list(self):
        # some args only in route info for scheduled routes
        route_skip = ['origin', 'destination', 'holidays', 'number_stations']
        test_url = urls.route_list()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=current_routes.text,
                               content_type='application/xml')
        routes = client.route_list()
        route = routes[0]
        self.assert_dictionary(route, skip=route_skip)

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
        self.assertTrue(len(route['stations']) > 0)
        station = route['stations'][0]
        self.assertTrue(isinstance(station, basestring))

    def test_station_list(self): #pylint: disable=no-self-use
        client.station_list()

    @httpretty.activate
    def test_station_info(self):
        station_abbr = 'rich'
        test_url = urls.station_info(station_abbr)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=station_info.text,
                               content_type='application/xml')
        station = client.station_info(station_abbr)
        self.assert_dictionary(station, skip=['north_platforms', 'north_routes'])

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
        first_time = station['schedule_times'][0]
        self.assert_dictionary(first_time)

    @httpretty.activate
    def test_schedule(self):
        test_url = urls.schedule_list()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=schedule_list.text,
                               content_type='application/xml')
        schedules = client.schedule_list()
        self.assertTrue(len(schedules) > 0)
        sched = schedules[0]
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
