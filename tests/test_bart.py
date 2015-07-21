from datetime import datetime
import httpretty

from transit.client import bart as client
from transit.urls import bart

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

class BartTestClient(utils.BaseTestClient): #pylint: disable=too-many-public-methods

    @httpretty.activate
    def test_bsa(self):
        test_url = bart.service_advisory()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=bsa.text,
                               content_type='application/xml')
        advisories = client.service_advisory()
        # should only be one advisory in data anyway
        adv = advisories[0]
        self.assert_all_variables(adv)
        desc = adv.description
        self.assertTrue(isinstance(desc, str))
        self.assertTrue(isinstance(adv.expires, datetime))

    @httpretty.activate
    def test_bsa_delay(self):
        test_url = bart.service_advisory()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=bsa_no_delay.text,
                               content_type='application/xml')
        advisories = client.service_advisory()
        # should only be one advisory in data anyway
        adv = advisories[0]
        self.assert_all_variables(adv, skip=['station', 'type', 'posted',
                                             'expires', 'id'])
        # find first description, make sure its a string
        desc = adv.description
        self.assertTrue(isinstance(desc, str))

    @httpretty.activate
    def test_train_count(self):
        test_url = bart.train_count()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=train_count.text,
                               content_type='application/xml')
        count = client.train_count()
        self.assertTrue(isinstance(count, int))

    @httpretty.activate
    def test_elevator_status(self):
        test_url = bart.elevator_status()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=elevator.text,
                               content_type='application/xml')
        status = client.elevator_status()
        self.assert_all_variables(status, skip=['expires'])
        desc = status.description
        self.assertTrue(isinstance(desc, str))

    @httpretty.activate
    def test_estimated_departures(self):
        station = 'rich'
        test_url = bart.estimated_departures(station)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=estimates.text,
                               content_type='application/xml')
        ests = client.station_departures(station)
        est = ests[0]
        self.assert_all_variables(est)
        self.assertEqual(station.lower(), est.abbreviation.lower())
        self.assertTrue(len(est.directions) > 1)
        direction = est.directions[0]
        self.assert_all_variables(direction)
        self.assertTrue(len(direction.estimates) > 0)
        direction_estimate = direction.estimates[0]
        self.assert_all_variables(direction_estimate)

        # test with destinations
        ests = client.station_departures(station,
                                         destinations=['frmt'])
        est = ests[0]
        self.assertEqual(len(est.directions), 1)


    @httpretty.activate
    def test_multiple_stations(self):
        station = 'all'
        test_url = bart.estimated_departures(station)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=estimate_all.text,
                               content_type='application/xml')
        ests = client.station_departures(station)
        self.assertTrue(len(ests) > 0)
        for est in ests:
            self.assert_all_variables(est)
            direction = est.directions[0]
            self.assert_all_variables(direction)
            self.assertTrue(len(direction.estimates) > 0)
            direction_estimate = direction.estimates[0]
            self.assert_all_variables(direction_estimate)

    @httpretty.activate
    def test_multiple_stations_custom(self):
        station = 'all'
        test_url = bart.estimated_departures(station)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=estimate_all.text,
                               content_type='application/xml')
        station_data = {
            'mont' : ['dubl', 'pitt'],
            'bayf' : [],
        }
        ests = client.multiple_station_departures(station_data)
        for est in ests:
            if est.abbreviation.lower() == 'mont':
                self.assertEqual(len(est.directions), 2)
            elif est.abbreviation.lower() == 'bayf':
                self.assertTrue(len(est.directions) > 0)
            self.assert_all_variables(est)
            direction = est.directions[0]
            self.assert_all_variables(direction)
            self.assertTrue(len(direction.estimates) > 0)
            direction_estimate = direction.estimates[0]
            self.assert_all_variables(direction_estimate)


    @httpretty.activate
    def test_current_route(self):
        # some args only in route info for scheduled routes
        route_skip = ['origin', 'destination', 'holidays', 'number_stations']
        test_url = bart.route_list()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=current_routes.text,
                               content_type='application/xml')
        routes = client.route_list()
        route = routes[0]
        self.assert_all_variables(route, skip=route_skip)

    @httpretty.activate
    def test_route_info(self):
        route_number = 35
        test_url = bart.route_show(route_number)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=route_info.text,
                               content_type='application/xml')
        route = client.route_show(route_number)
        self.assert_all_variables(route)
        self.assertTrue(len(route.stations) > 0)
        station = route.stations[0]
        self.assertTrue(isinstance(station, str))

    def test_station_list(self): #pylint: disable=no-self-use
        client.station_list()

    @httpretty.activate
    def test_station_info(self):
        station_abbr = '24th'
        test_url = bart.station_info(station_abbr)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=station_info.text,
                               content_type='application/xml')
        station = client.station_info(station_abbr)
        self.assert_all_variables(station)

    @httpretty.activate
    def test_station_access(self):
        station_abbr = '12th'
        test_url = bart.station_access(station_abbr)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=station_access.text,
                               content_type='application/xml')
        station = client.station_access(station_abbr)
        self.assert_all_variables(station)

    @httpretty.activate
    def test_station_schedule(self):
        station_abbr = '12th'
        test_url = bart.station_schedule(station_abbr)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=station_schedule.text,
                               content_type='application/xml')
        station = client.station_schedule(station_abbr)
        self.assert_all_variables(station)
        self.assertTrue(len(station.schedule_times) > 0)
        first_time = station.schedule_times[0]
        self.assert_all_variables(first_time)

    @httpretty.activate
    def test_schedule(self):
        test_url = bart.schedule_list()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=schedule_list.text,
                               content_type='application/xml')
        schedules = client.schedule_list()
        self.assertTrue(len(schedules) > 0)
        sched = schedules[0]
        self.assert_all_variables(sched)

    @httpretty.activate
    def test_schedule_fare(self):
        origin = '12th'
        dest = 'embr'
        test_url = bart.schedule_fare(origin, dest)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=schedule_fare.text,
                               content_type='application/xml')
        fare = client.schedule_fare(origin, dest)
        self.assert_all_variables(fare)
