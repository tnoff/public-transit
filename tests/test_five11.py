import json

import pytest

from transit.modules.five11 import client
from transit.modules.five11 import urls
from transit.exceptions import TransitException

from tests.data.five11.lines import DATA as lines
from tests.data.five11.operators import DATA as operators
from tests.data.five11.stop_monitoring import DATA as stop_monitoring
from tests.data.five11.stops import DATA as stops


FAKE_KEY = 'abc1234'


def test_operators(requests_mock):
    requests_mock.get(urls.operators(FAKE_KEY), json=operators)
    ops = client.operators(FAKE_KEY)
    for operator in ops:
        assert operator['Id'] is not None
        assert operator['Name'] is not None


def test_lines(requests_mock):
    requests_mock.get(urls.lines(FAKE_KEY, 'SC'), json=lines)
    resp = client.lines(FAKE_KEY, 'SC')
    for line in resp:
        assert line['Id'] is not None
        assert line['Name'] is not None


def test_stops(requests_mock):
    requests_mock.get(urls.stops(FAKE_KEY, 'SC'), json=stops)
    resp = client.stops(FAKE_KEY, 'SC')
    stop_points = resp['Contents']['dataObjects']['ScheduledStopPoint']
    assert stop_points[0]['id'] == '70021'


def test_stops_line_id(requests_mock):
    # line_id filter builds a distinct url (spaces are url-encoded)
    requests_mock.get(urls.stops(FAKE_KEY, 'SC', line_id='Rapid 522'), json=stops)
    resp = client.stops(FAKE_KEY, 'SC', line_id='Rapid 522')
    assert 'Contents' in resp


def test_stop_monitoring(requests_mock):
    requests_mock.get(urls.stop_monitoring(FAKE_KEY, 'SC', '70021'), json=stop_monitoring)
    resp = client.stop_monitoring(FAKE_KEY, 'SC', '70021')
    assert 'ServiceDelivery' in resp


def test_stop_monitoring_all(requests_mock):
    # agency-wide call (no stop code) — exercises the no-stopcode url branch
    requests_mock.get(urls.stop_monitoring(FAKE_KEY, 'SC'), json=stop_monitoring)
    resp = client.stop_monitoring(FAKE_KEY, 'SC')
    assert 'ServiceDelivery' in resp


def test_stop_monitoring_strips_bom(requests_mock):
    # 511 prefixes responses with a UTF-8 BOM; make sure parsing survives it
    requests_mock.get(urls.stop_monitoring(FAKE_KEY, 'SC', '70021'),
                      text='\ufeff' + json.dumps(stop_monitoring))
    resp = client.stop_monitoring(FAKE_KEY, 'SC', '70021')
    assert 'ServiceDelivery' in resp


def test_request_error(requests_mock):
    # 404 is not retryable — raises immediately
    requests_mock.get(urls.operators(FAKE_KEY), status_code=404, text='error')
    with pytest.raises(TransitException):
        client.operators(FAKE_KEY)


def test_invalid_operator_412(requests_mock, mocker):
    # 511 returns 412 for an unknown/mis-cased operator id — not retried,
    # and surfaced as an actionable message
    sleep = mocker.patch('transit.modules.five11.client.time.sleep')
    requests_mock.get(urls.lines(FAKE_KEY, 'ZZ'), status_code=412, text='<html>412</html>')
    with pytest.raises(TransitException) as e:
        client.lines(FAKE_KEY, 'ZZ')
    assert 'operators' in str(e.value)
    assert sleep.call_count == 0  # 412 is a client error, not retried


def test_operator_case_normalized(requests_mock):
    # lowercase operator is normalized to the case-sensitive 511 id
    requests_mock.get(urls.lines(FAKE_KEY, 'SC'), json=lines)
    assert client.lines(FAKE_KEY, 'sc') == lines


def test_retry_then_success(requests_mock, mocker):
    # transient 5xx should recover on retry
    mocker.patch('transit.modules.five11.client.time.sleep')
    requests_mock.get(urls.operators(FAKE_KEY), [
        {'status_code': 503, 'text': 'unavailable'},
        {'json': operators, 'status_code': 200},
    ])
    assert client.operators(FAKE_KEY) == operators


def test_retry_exhausted(requests_mock, mocker):
    sleep = mocker.patch('transit.modules.five11.client.time.sleep')
    requests_mock.get(urls.operators(FAKE_KEY), status_code=503, text='unavailable')
    with pytest.raises(TransitException):
        client.operators(FAKE_KEY)
    assert sleep.call_count == 2  # retried RETRIES-1 times before giving up


def test_stop_visits():
    visits = client.stop_visits(stop_monitoring)
    assert len(visits) == 2
    assert visits[0]['stop_code'] == '70021'
    assert visits[0]['stop_title'] == 'El Camino Real & Palo Alto Ave'
    assert visits[0]['line'] == '22'
    assert visits[0]['destination'] == 'Palo Alto Transit Center'
    assert visits[0]['expected_arrival'] == '2099-01-01T00:05:00Z'


def test_stop_visits_single():
    # SIRI collapses a single result to a dict — exercise the normalize branch
    single = {
        'ServiceDelivery': {
            'StopMonitoringDelivery': {
                'MonitoredStopVisit': {
                    'MonitoringRef': '70021',
                    'MonitoredVehicleJourney': {
                        'LineRef': '22',
                        'DestinationName': 'Palo Alto Transit Center',
                        'MonitoredCall': {
                            'StopPointName': 'El Camino Real & Palo Alto Ave',
                            'ExpectedArrivalTime': '2099-01-01T00:05:00Z',
                        },
                    },
                }
            }
        }
    }
    visits = client.stop_visits(single)
    assert len(visits) == 1
    assert visits[0]['line'] == '22'


def test_stop_visits_empty():
    empty = {'ServiceDelivery': {'StopMonitoringDelivery': {}}}
    assert client.stop_visits(empty) == []
