from transit.modules.nextbus import client
from transit.exceptions import TransitException
from transit.modules.nextbus import urls

from tests.data.nextbus.agency_list import text as agency_list
from tests.data.nextbus.route_list import text as route_list
from tests.data.nextbus.route_show import text as route_show
from tests.data.nextbus.stop_predictions import text as stop_predictions
from tests.data.nextbus.message_get import text as message_get
from tests.data.nextbus.multi_predict_two import text as multi_two


def test_agency_list(requests_mock):
    requests_mock.get(urls.agency_list(), text=agency_list)
    agencies = client.agency_list()
    for agency in agencies['agency']:
        assert agency['tag'] != None
        assert agency['title'] != None
        assert agency['regionTitle'] != None

def test_route_list(requests_mock):
    agency_tag = 'sf-muni'
    requests_mock.get(urls.route_list(agency_tag), text=route_list)
    routes = client.route_list(agency_tag)
    for route in routes['route']:
        assert route['tag'] != None
        assert route['title'] != None

def test_route_show(requests_mock):
    agency_tag = 'actransit'
    route_tag = '801'    
    requests_mock.get(urls.route_show(agency_tag, route_tag), text=route_show)
    route = client.route_show(agency_tag, route_tag)
    assert route['route']['tag'] != None
    for stop in route['route']['stop']:
        assert stop['tag'] != None

def test_stop_predictions(requests_mock):
    agency_tag = 'actransit'
    stop_id = '51303'
    requests_mock.get(urls.stop_prediction(agency_tag, stop_id), text=stop_predictions)
    predictions = client.stop_prediction(agency_tag, stop_id)
    for pred in predictions['predictions']:
        assert pred['routeTag'] != None
        assert pred['direction']['prediction']['seconds'] != None

def test_stop_prediction_with_route_multi(requests_mock):
    agency_tag = 'actransit'
    stop_id = '51303'
    route_tags = ['22', '99']
    requests_mock.get(urls.stop_prediction(agency_tag, stop_id, route_tags=route_tags), text=stop_predictions)
    predictions = client.stop_prediction(agency_tag, stop_id, route_tags=route_tags)
    for pred in predictions['predictions']:
        assert pred['routeTag'] != None
        assert pred['direction']['prediction']['seconds'] != None

def test_message(requests_mock):
    agency_tag = 'sf-muni'
    route_tag = '38'
    requests_mock.get(urls.message_get(agency_tag, route_tag), text=message_get)
    routes = client.route_messages(agency_tag, route_tag)
    assert routes['route']['tag'] != None
    for mess in routes['route']['message']:
        assert mess['id'] != None

def test_multiple_prediction(requests_mock):
    agency_tag = 'sf-muni'
    data = {'13568' : ['38',], '13567' : ['38']}    
    requests_mock.get(urls.multiple_stop_prediction(agency_tag, data), text=multi_two)
    preds = client.stop_multiple_predictions(agency_tag, data)
    for pred in preds['predictions']:
        assert pred['routeTag'] != None
        assert pred['direction']['prediction'][0]['seconds'] != None