import httpretty

from tests import utils
from tests.data.bart import estimates
from tests.data.bart import route_info as route_info4
from tests.data.bart import route_info7
from tests.data.bart import station_info
from tests.data.nextbus import stop_predictions
from tests.data.nextbus import route_show

from trip_planner.client import TripPlanner
from transit.modules.bart import urls as bart_urls
from transit.modules.nextbus import urls as nextbus_urls

class TestPlanner(utils.BaseTestClient):

    @httpretty.activate
    def test_basic(self):
        agency = 'actransit'
        stop_id = '51303'
        route_tags = '22'
        with utils.temp_database() as db:
            client = TripPlanner(db)
            route_url = nextbus_urls.route_show(agency, route_tags)
            httpretty.register_uri(httpretty.GET,
                                   route_url,
                                   body=route_show.text,
                                   content_type='application/xml')
            stop_url = nextbus_urls.stop_prediction(agency, stop_id, route_tags=route_tags)
            httpretty.register_uri(httpretty.GET,
                                   stop_url,
                                   body=stop_predictions.text,
                                   content_type='application/xml')
            leg1 = client.leg_create(agency, stop_id, destinations=route_tags)
            self.assert_dictionary(leg1)
            # httpretty can be weird, set it again to make sure
            httpretty.register_uri(httpretty.GET,
                                   stop_url,
                                   body=stop_predictions.text,
                                   content_type='application/xml')
            agency_tag, output = client.leg_show(leg1['id'])
            self.assertEqual(agency_tag, agency)
            self.assert_dictionary(output[0])

            agency2 = 'bart'
            bart_stop = 'rich'
            directions = ['frmt']
            station_url = bart_urls.station_info(bart_stop)
            httpretty.register_uri(httpretty.GET,
                                   station_url,
                                   body=station_info.text,
                                   content_type='application/xml')
            route4_url = bart_urls.route_info('4')
            httpretty.register_uri(httpretty.GET,
                                   route4_url,
                                   body=route_info4.text,
                                   content_type='application/xml')
            route7_url = bart_urls.route_info('7')
            httpretty.register_uri(httpretty.GET,
                                   route7_url,
                                   body=route_info7.text,
                                   content_type='application/xml')
            leg2 = client.leg_create(agency2, bart_stop, destinations=directions)
            self.assert_dictionary(leg2, skip=['stop_tag'])

            estimate_url = bart_urls.estimated_departures(bart_stop)
            httpretty.register_uri(httpretty.GET,
                                   estimate_url,
                                   body=estimates.text,
                                   content_type='application/xml')
            bart_tag, output2 = client.leg_show(leg2['id'])
            self.assertEqual(bart_tag, agency2)
            self.assert_dictionary(output2[0])

            trip = client.trip_create('foo', [leg1['id'], leg2['id']])
            self.assert_dictionary(trip)

            client.trip_delete(trip['id'])

            client.leg_delete(leg1['id'])
            client.leg_delete(leg2['id'])
