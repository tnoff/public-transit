from datetime import datetime
import httpretty
import unittest

from transit import client
from transit.urls import bart

from tests.data.bart import bsa
from tests.data.bart import bsa_no_delay
from tests.data.bart import train_count
from tests.data.bart import elevator
from tests.data.bart import estimates
from tests.data.bart import current_routes

class BartTestClient(unittest.TestCase):

    def assert_all_variables(self, obj, skip=[]):
        # assert all variables in object are not none
        keys = vars(obj).keys()
        real_keys = list(set(keys) - set(skip))
        for key in real_keys:
            self.assertNotEqual(getattr(obj, key), None)

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
        ests = client.bart.estimated_departures(station)
        est = ests[0]
        self.assert_all_variables(est)
        self.assertEqual(station.lower(), est.station_abbreviation.lower())
        self.assertTrue(len(est.directions) > 0)
        direction = est.directions[0]
        self.assert_all_variables(direction)
        self.assertTrue(len(direction.estimates) > 0)
        direction_estimate = direction.estimates[0]
        self.assert_all_variables(direction_estimate)

    @httpretty.activate
    def test_current_route(self):
        test_url = bart.current_routes()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=current_routes.text,
                               content_type='application/xml')
        schedule = client.bart.current_routes()
        self.assert_all_variables(schedule)
        self.assertTrue(len(schedule.routes) > 0)
        route = schedule.routes[0]
        self.assert_all_variables(route)
