import time

import requests

from transit.exceptions import TransitException
from transit.modules.five11 import urls

# 511's IIS gateway can return transient 5xx under load, so retry those.
# NOTE: 412 is NOT transient — 511 returns it for an unknown/mis-cased
# operator id (operator ids are case-sensitive, e.g. 'SC' for VTA), so it
# gets a dedicated, actionable error instead of a retry.
RETRY_STATUS = {500, 502, 503, 504}
RETRIES = 3
BACKOFF_SECONDS = 0.5

def _make_request(url: str) -> dict:
    resp = None
    for attempt in range(RETRIES):
        if attempt:
            time.sleep(BACKOFF_SECONDS * attempt)
        resp = requests.get(url, timeout=120)
        if resp.status_code == 200:
            # 511 prefixes JSON responses with a UTF-8 BOM that breaks strict parsing
            resp.encoding = 'utf-8-sig'
            return resp.json()
        if resp.status_code not in RETRY_STATUS:
            break
    if resp.status_code == 412:
        raise TransitException(
            'Got 412 from 511 — usually an unknown or mis-cased operator id '
            '(they are case-sensitive, e.g. "SC" for VTA). Run `five11 operators` '
            'to list valid ids.')
    raise TransitException(f'Non 200 status code {resp.status_code} returned, "{resp.text}"')

def operators(five11_api_key: str) -> list:
    '''
    List 511 transit operators (use to find an operator id)

    five11_api_key  :   511.org API key
    '''
    url = urls.operators(five11_api_key)
    return _make_request(url)

def lines(five11_api_key: str, operator: str) -> list:
    '''
    List an operator's lines (routes)

    five11_api_key  :   511.org API key
    operator        :   511 operator id (e.g. 'SC' for VTA)
    '''
    url = urls.lines(five11_api_key, operator.upper())
    return _make_request(url)

def stops(five11_api_key: str, operator: str, line_id: str | None = None) -> dict:
    '''
    List an operator's stops (stop codes, names, locations)

    five11_api_key  :   511.org API key
    operator        :   511 operator id (e.g. 'SC' for VTA)
    line_id         :   Filter to a single line id (e.g. '22', 'Orange Line')
    '''
    url = urls.stops(five11_api_key, operator.upper(), line_id=line_id)
    return _make_request(url)

def stop_monitoring(five11_api_key: str, operator: str, stop_code: str | None = None) -> dict:
    '''
    Real time stop departures for a 511 operator

    five11_api_key  :   511.org API key
    operator        :   511 operator id (e.g. 'SC' for VTA)
    stop_code       :   Limit results to a single stop code
    '''
    url = urls.stop_monitoring(five11_api_key, operator.upper(), stop_code=stop_code)
    return _make_request(url)

def stop_visits(response: dict) -> list[dict]:
    '''
    Flatten a StopMonitoring response into a list of departure dicts

    response        :   Parsed StopMonitoring response
    '''
    delivery = response['ServiceDelivery']['StopMonitoringDelivery']
    visits = delivery.get('MonitoredStopVisit', [])
    # SIRI collapses a single result to a dict instead of a list
    if isinstance(visits, dict):
        visits = [visits]
    departures = []
    for visit in visits:
        journey = visit['MonitoredVehicleJourney']
        call = journey['MonitoredCall']
        departures.append({
            'stop_code': visit['MonitoringRef'],
            'stop_title': call['StopPointName'],
            'line': journey['LineRef'],
            'destination': journey['DestinationName'],
            'expected_arrival': call['ExpectedArrivalTime'],
        })
    return departures
