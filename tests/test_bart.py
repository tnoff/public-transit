from datetime import datetime
import httpretty

from transit import client
from transit.urls import bart

from tests import utils

from tests.data.bart import bsa
from tests.data.bart import bsa_no_delay
from tests.data.bart import train_count
from tests.data.bart import elevator
from tests.data.bart import estimates
from tests.data.bart import current_routes
from tests.data.bart import route_info
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
        advisories = client.bart.service_advisory()
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
        advisories = client.bart.service_advisory()
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
        count = client.bart.train_count()
        self.assertTrue(isinstance(count, int))

    @httpretty.activate
    def test_elevator_status(self):
        test_url = bart.elevator_status()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=elevator.text,
                               content_type='application/xml')
        status = client.bart.elevator_status()
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
        ests = client.bart.station_departures(station)
        est = ests[0]
        self.assert_all_variables(est)
        self.assertEqual(station.lower(), est.abbreviation.lower())
        self.assertTrue(len(est.directions) > 0)
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
        routes = client.bart.route_list()
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
        route = client.bart.route_show(route_number)
        self.assert_all_variables(route)
        self.assertTrue(len(route.stations) > 0)
        station = route.stations[0]
        self.assertTrue(isinstance(station, str))

    def test_station_list(self): #pylint: disable=no-self-use
        client.bart.station_list()

    @httpretty.activate
    def test_station_info(self):
        station_abbr = '24th'
        test_url = bart.station_info(station_abbr)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=station_info.text,
                               content_type='application/xml')
        station = client.bart.station_info(station_abbr)
        self.assert_all_variables(station)

    @httpretty.activate
    def test_station_access(self):
        station_abbr = '12th'
        test_url = bart.station_access(station_abbr)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=station_access.text,
                               content_type='application/xml')
        station = client.bart.station_access(station_abbr)
        self.assert_all_variables(station)

    @httpretty.activate
    def test_station_schedule(self):
        station_abbr = '12th'
        test_url = bart.station_schedule(station_abbr)
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=station_schedule.text,
                               content_type='application/xml')
        station = client.bart.station_schedule(station_abbr)
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
        schedules = client.bart.schedule_list()
        self.assertTrue(len(schedules) > 0)
        sched = schedules[0]
        self.assert_all_variables(sched)
