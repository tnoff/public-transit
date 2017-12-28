import httpretty

from tests import utils

from tests.data.planner import bart_estimates_all
from tests.data.planner import bart_estimated_wdub
from tests.data.planner import nextbus_invalid_stop
from tests.data.planner import nextbus_multiple_estimate
from tests.data.planner import nextbus_stop_51303
from tests.data.planner import nextbus_route_22
from tests.data.planner import station_info_wdub
from tests.data.planner import route_info_11
from tests.data.planner import route_info_12

from transit.modules.bart import urls as bart_urls
from transit.modules.nextbus import urls as nextbus_urls

from trip_planner.client import TripPlanner
from trip_planner.exceptions import TripPlannerException

class TestPlanner(utils.BaseTestClient):

    def test_leg_create_bart_invalid_station(self):
        client = TripPlanner()
        with self.assertRaises(TripPlannerException) as error:
            client.leg_create('bart', 'foobar')
        self.assertTrue('Bart station not valid:foobar' in error.exception)

    @httpretty.activate
    def test_leg_create_bart(self):
        client = TripPlanner()
        station = 'wdub'
        # first call is station info
        station_info_url = bart_urls.station_info(station)
        httpretty.register_uri(httpretty.GET,
                               station_info_url,
                               body=station_info_wdub.text,
                               content_type='application/xml')
        # then return route infos, route list given in station info
        route1 = 12
        route2 = 11
        route1_info_url = bart_urls.route_info(route1)
        httpretty.register_uri(httpretty.GET,
                               route1_info_url,
                               body=route_info_12.text,
                               content_type='application/xml')
        route2_info_url = bart_urls.route_info(route2)
        httpretty.register_uri(httpretty.GET,
                               route2_info_url,
                               body=route_info_11.text,
                               content_type='application/xml')
        # create station with no includes, make sure populated correctly
        leg = client.leg_create('bart', station)
        self.assertEqual(sorted(["daly", "dubl"]), sorted(leg['includes']))

    @httpretty.activate
    def test_leg_create_bart_invalid_destinations(self):
        client = TripPlanner()
        station = 'wdub'
        # first call is station info
        station_info_url = bart_urls.station_info(station)
        httpretty.register_uri(httpretty.GET,
                               station_info_url,
                               body=station_info_wdub.text,
                               content_type='application/xml')
        # then return route infos, route list given in station info
        route1 = 12
        route2 = 11
        route1_info_url = bart_urls.route_info(route1)
        httpretty.register_uri(httpretty.GET,
                               route1_info_url,
                               body=route_info_12.text,
                               content_type='application/xml')
        route2_info_url = bart_urls.route_info(route2)
        httpretty.register_uri(httpretty.GET,
                               route2_info_url,
                               body=route_info_11.text,
                               content_type='application/xml')
        # create station with no includes, make sure populated correctly
        with self.assertRaises(TripPlannerException) as error:
            client.leg_create('bart', station, destinations=['foo'])
        self.assertTrue('Invalid destination:foo' in error.exception)

    @httpretty.activate
    def test_leg_create_bart_one_destination(self):
        # make sure if given one destination, only that one and not both are used
        client = TripPlanner()
        station = 'wdub'
        # first call is station info
        station_info_url = bart_urls.station_info(station)
        httpretty.register_uri(httpretty.GET,
                               station_info_url,
                               body=station_info_wdub.text,
                               content_type='application/xml')
        # then return route infos, route list given in station info
        route1 = 12
        route2 = 11
        route1_info_url = bart_urls.route_info(route1)
        httpretty.register_uri(httpretty.GET,
                               route1_info_url,
                               body=route_info_12.text,
                               content_type='application/xml')
        route2_info_url = bart_urls.route_info(route2)
        httpretty.register_uri(httpretty.GET,
                               route2_info_url,
                               body=route_info_11.text,
                               content_type='application/xml')
        # create station with no includes, make sure populated correctly
        leg = client.leg_create('bart', station, destinations=['dubl'])
        self.assertEqual(leg['includes'], ['dubl'])

    @httpretty.activate
    def test_leg_show_bart(self):
        client = TripPlanner()
        station = 'wdub'

        leg = client.leg_create('bart', station,
                                destinations=['daly', 'dubl'], force=True)

        departure_url = bart_urls.estimated_departures(station)
        httpretty.register_uri(httpretty.GET,
                               departure_url,
                               body=bart_estimated_wdub.text,
                               content_type='application/xml')
        shown_agency, shown_data = client.leg_show(leg['id'])
        self.assertEqual(shown_agency, 'bart')
        for station in shown_data:
            for direction in station['directions']:
                self.assertTrue(len(direction['estimates']) > 0)

    @httpretty.activate
    def test_leg_create_nextbus_invalid_stop(self):
        client = TripPlanner()
        stop_url = nextbus_urls.stop_prediction('actransit', 'foo')
        httpretty.register_uri(httpretty.GET,
                               stop_url,
                               body=nextbus_invalid_stop.text,
                               content_type='text/xml')
        with self.assertRaises(TripPlannerException) as error:
            client.leg_create('actransit', 'foo')
        self.assertTrue('Could not identify stop:stopId "foo" is not a '\
                        'valid stop id integer' in error.exception)

    @httpretty.activate
    def test_leg_create_nextbus(self):
        client = TripPlanner()
        agency = 'actransit'
        stop = '51303'
        route = 22
        route_url = nextbus_urls.route_show(agency, route)
        stop_url = nextbus_urls.stop_prediction(agency, stop)
        httpretty.register_uri(httpretty.GET,
                               route_url,
                               body=nextbus_route_22.text,
                               content_type='text/xml')
        httpretty.register_uri(httpretty.GET,
                               stop_url,
                               body=nextbus_stop_51303.text,
                               content_type='text/xml')
        leg = client.leg_create(agency, stop)
        self.assertEqual(sorted(leg['includes']), ['22', '801', '99'])

    @httpretty.activate
    def test_leg_create_nextbus_invalid_destination(self):
        client = TripPlanner()
        agency = 'actransit'
        stop = '51303'
        route = 22
        route_url = nextbus_urls.route_show(agency, route)
        stop_url = nextbus_urls.stop_prediction(agency, stop)
        httpretty.register_uri(httpretty.GET,
                               route_url,
                               body=nextbus_route_22.text,
                               content_type='text/xml')
        httpretty.register_uri(httpretty.GET,
                               stop_url,
                               body=nextbus_stop_51303.text,
                               content_type='text/xml')
        with self.assertRaises(TripPlannerException) as error:
            client.leg_create(agency, stop, destinations='100')
        self.assertTrue('Invalid route given:100' in error.exception)

    @httpretty.activate
    def test_leg_create_nextbus_invalid_destinations(self):
        client = TripPlanner()
        agency = 'actransit'
        stop = '51303'
        route = 22
        route_url = nextbus_urls.route_show(agency, route)
        stop_url = nextbus_urls.stop_prediction(agency, stop)
        httpretty.register_uri(httpretty.GET,
                               route_url,
                               body=nextbus_route_22.text,
                               content_type='text/xml')
        httpretty.register_uri(httpretty.GET,
                               stop_url,
                               body=nextbus_stop_51303.text,
                               content_type='text/xml')
        with self.assertRaises(TripPlannerException) as error:
            client.leg_create(agency, stop, destinations=['100'])
        self.assertTrue('Invalid route given:100' in error.exception)

    @httpretty.activate
    def test_leg_create_nextbus_one_direction(self):
        client = TripPlanner()
        agency = 'actransit'
        stop = '51303'
        route = '22'
        route_url = nextbus_urls.route_show(agency, route)
        stop_url = nextbus_urls.stop_prediction(agency, stop)
        httpretty.register_uri(httpretty.GET,
                               route_url,
                               body=nextbus_route_22.text,
                               content_type='text/xml')
        httpretty.register_uri(httpretty.GET,
                               stop_url,
                               body=nextbus_stop_51303.text,
                               content_type='text/xml')
        leg = client.leg_create(agency, stop, destinations=[route])
        self.assertEqual(leg['includes'], ['22'])

    @httpretty.activate
    def test_leg_list(self):
        client = TripPlanner()
        agency = 'actransit'
        stop = '51303'
        route = '22'
        route_url = nextbus_urls.route_show(agency, route)
        stop_url = nextbus_urls.stop_prediction(agency, stop)
        httpretty.register_uri(httpretty.GET,
                               route_url,
                               body=nextbus_route_22.text,
                               content_type='text/xml')
        httpretty.register_uri(httpretty.GET,
                               stop_url,
                               body=nextbus_stop_51303.text,
                               content_type='text/xml')
        client.leg_create(agency, stop)
        legs = client.leg_list()
        self.assertEqual(len(legs), 1)

    @httpretty.activate
    def test_leg_delete(self):
        client = TripPlanner()
        agency = 'actransit'
        stop = '51303'
        route = '22'
        route_url = nextbus_urls.route_show(agency, route)
        stop_url = nextbus_urls.stop_prediction(agency, stop)
        httpretty.register_uri(httpretty.GET,
                               route_url,
                               body=nextbus_route_22.text,
                               content_type='text/xml')
        httpretty.register_uri(httpretty.GET,
                               stop_url,
                               body=nextbus_stop_51303.text,
                               content_type='text/xml')
        client.leg_create(agency, stop)
        legs = client.leg_list()
        self.assertEqual(len(legs), 1)
        client.leg_delete(1)
        legs = client.leg_list()
        self.assertEqual(len(legs), 0)

    @httpretty.activate
    def test_leg_delete_with_trip_is_invalid(self):
        client = TripPlanner()
        agency = 'actransit'
        stop = '51303'
        route = '22'
        route_url = nextbus_urls.route_show(agency, route)
        stop_url = nextbus_urls.stop_prediction(agency, stop)
        httpretty.register_uri(httpretty.GET,
                               route_url,
                               body=nextbus_route_22.text,
                               content_type='text/xml')
        httpretty.register_uri(httpretty.GET,
                               stop_url,
                               body=nextbus_stop_51303.text,
                               content_type='text/xml')
        leg = client.leg_create(agency, stop)
        client.trip_create('foo', [leg['id']])
        with self.assertRaises(TripPlannerException) as error:
            client.leg_delete(leg['id'])
        self.assertTrue('Cannot delete leg, being used by a Trip:1' in error.exception)

    @httpretty.activate
    def test_leg_show_nextbus(self):
        client = TripPlanner()
        agency = 'actransit'
        stop = '51303'
        route = '22'
        route_url = nextbus_urls.route_show(agency, route)
        stop_url = nextbus_urls.stop_prediction(agency, stop)
        httpretty.register_uri(httpretty.GET,
                               route_url,
                               body=nextbus_route_22.text,
                               content_type='text/xml')
        httpretty.register_uri(httpretty.GET,
                               stop_url,
                               body=nextbus_stop_51303.text,
                               content_type='text/xml')
        leg = client.leg_create(agency, stop)
        httpretty.register_uri(httpretty.GET,
                               stop_url,
                               body=nextbus_stop_51303.text,
                               content_type='text/xml')
        shown_agency, shown_data = client.leg_show(leg['id'])
        self.assertEqual(shown_agency, agency)
        for route in shown_data:
            for direction in route['directions']:
                self.assertTrue(len(direction['predictions']) > 0)

    @httpretty.activate
    def test_trip_create(self):
        client = TripPlanner()
        agency = 'actransit'
        stop = '51303'
        route = '22'
        route_url = nextbus_urls.route_show(agency, route)
        stop_url = nextbus_urls.stop_prediction(agency, stop)
        httpretty.register_uri(httpretty.GET,
                               route_url,
                               body=nextbus_route_22.text,
                               content_type='text/xml')
        httpretty.register_uri(httpretty.GET,
                               stop_url,
                               body=nextbus_stop_51303.text,
                               content_type='text/xml')
        leg = client.leg_create(agency, stop)
        trip = client.trip_create('foo', int(leg['id']))
        self.assertEqual(trip['legs'], [leg['id']])

    @httpretty.activate
    def test_trip_list(self):
        client = TripPlanner()
        agency = 'actransit'
        stop = '51303'
        route = '22'
        route_url = nextbus_urls.route_show(agency, route)
        stop_url = nextbus_urls.stop_prediction(agency, stop)
        httpretty.register_uri(httpretty.GET,
                               route_url,
                               body=nextbus_route_22.text,
                               content_type='text/xml')
        httpretty.register_uri(httpretty.GET,
                               stop_url,
                               body=nextbus_stop_51303.text,
                               content_type='text/xml')
        leg1 = client.leg_create(agency, stop)

        station = 'wdub'
        leg2 = client.leg_create('bart', station, destinations=['daly', 'dubl'], force=True)

        client.trip_create('foo', [int(leg1['id']), int(leg2['id'])])
        trips = client.trip_list()
        self.assertEqual(len(trips), 1)
        self.assertEqual(sorted(trips[1]['legs']), [1, 2])

    @httpretty.activate
    def test_trip_delete(self):
        client = TripPlanner()
        agency = 'actransit'
        stop = '51303'
        route = '22'
        route_url = nextbus_urls.route_show(agency, route)
        stop_url = nextbus_urls.stop_prediction(agency, stop)
        httpretty.register_uri(httpretty.GET,
                               route_url,
                               body=nextbus_route_22.text,
                               content_type='text/xml')
        httpretty.register_uri(httpretty.GET,
                               stop_url,
                               body=nextbus_stop_51303.text,
                               content_type='text/xml')
        leg1 = client.leg_create(agency, stop)
        trip = client.trip_create('foo', [int(leg1['id'])])
        client.trip_delete(trip['id'])
        trips = client.trip_list()
        self.assertEqual(len(trips), 0)

    @httpretty.activate
    def test_trip_show(self):
        client = TripPlanner()
        agency = 'actransit'
        stop = '51303'
        route = '22'
        route_url = nextbus_urls.route_show(agency, route)
        stop_url = nextbus_urls.stop_prediction(agency, stop)
        httpretty.register_uri(httpretty.GET,
                               route_url,
                               body=nextbus_route_22.text,
                               content_type='text/xml')
        httpretty.register_uri(httpretty.GET,
                               stop_url,
                               body=nextbus_stop_51303.text,
                               content_type='text/xml')
        leg1 = client.leg_create(agency, stop, destinations=['99', '22'])

        station = 'wdub'
        leg2 = client.leg_create('bart', station, destinations=['daly', 'dubl'], force=True)

        trip = client.trip_create('foo', [leg1['id'], leg2['id']])

        httpretty.register_uri(httpretty.GET,
                               bart_urls.estimated_departures('all'),
                               body=bart_estimates_all.text,
                               content_type='application/xml')
        httpretty.register_uri(httpretty.GET,
                               nextbus_urls.multiple_stop_prediction(agency,
                                                                     {'9902820' : ['22', '99']}),
                               body=nextbus_multiple_estimate.text,
                               content_type='application/xml')
        results = client.trip_show(trip['id'])

        self.assertTrue(len(results['bart']) > 0)
        for station in results['bart']: #pylint:disable=not-an-iterable
            for direction in station['directions']:
                self.assertTrue(len(direction['estimates']) > 0)
                for estimate in direction['estimates']:
                    self.assertNotEqual(estimate['minutes'], None)

        self.assertTrue(len(results['nextbus'].keys()) > 0)
        for agency, stop_data in results['nextbus'].items():
            for stop in stop_data:
                self.assertTrue(len(stop['directions']) > 0)
                for direction in stop['directions']:
                    self.assertTrue(len(direction['predictions']) > 0)
