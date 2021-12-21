from transit.modules.bart import client
from transit.modules.bart import urls

from tests.data.bart.service_advisory import DATA as service_advisory
from tests.data.bart.train_count import DATA as train_count
from tests.data.bart.elevator_status import DATA as elevator_status
from tests.data.bart.station_list import DATA as station_list
from tests.data.bart.station_departures import DATA as station_departures

FAKE_KEY = 'foobar1234'

def test_service_advisory(requests_mock):
    requests_mock.get(urls.service_advisory(FAKE_KEY), json=service_advisory)
    resp = client.service_advisory(FAKE_KEY)
    assert resp['date'] == '12/20/2021'
    assert resp['time'] == '19:39:00 PM PST'
    assert len(resp['bsa']) > 0

def test_train_count(requests_mock):
    requests_mock.get(urls.train_count(FAKE_KEY), json=train_count)
    resp = client.train_count(FAKE_KEY)
    assert resp['date'] == '12/20/2021'
    assert resp['time'] == '19:46:00 PM PST'
    assert resp['traincount'] == '44'

def test_elevator_status(requests_mock):
    requests_mock.get(urls.elevator_status(FAKE_KEY), json=elevator_status)
    resp = client.elevator_status(FAKE_KEY)
    assert resp['date'] == '12/20/2021'
    assert resp['time'] == '07:57:20 PM PST'
    assert len(resp['bsa']) > 0

def test_station_list(requests_mock):
    requests_mock.get(urls.station_list(FAKE_KEY), json=station_list)
    resp = client.station_list(FAKE_KEY)
    assert len(resp['stations']) > 0
    assert resp['stations']['station'][0]['abbr'] == '12TH'

def test_station_departures(requests_mock):
    requests_mock.get(urls.station_departures(FAKE_KEY, 'all'), json=station_departures)
    resp = client.station_departures(FAKE_KEY, 'all')
    assert len(resp['station']) > 0
    assert resp['station'][0]['abbr'] == 'LAKE'
    assert len(resp['station'][0]['etd']) > 0
    assert resp['station'][0]['etd'][0]['destination'] == 'Berryessa'
    assert len(resp['station'][0]['etd'][0]['estimate']) > 0
    assert resp['station'][0]['etd'][0]['estimate'][0]['minutes'] == '5'