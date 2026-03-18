import pytest

from transit.exceptions import TransitException
from trip_planner.client import TripPlanner
from trip_planner.exceptions import TripPlannerException

MOCK_BART_STATION_LIST = {
    'stations': {
        'station': [
            {
                "name": "West Oakland",
                "abbr": "WOAK",
                "gtfs_latitude": "37.804872",
                "gtfs_longitude": "-122.295140",
                "address": "1451 7th Street",
                "city": "Oakland",
                "county": "alameda",
                "state": "CA",
                "zipcode": "94607"
            }
        ]
    }
}

MOCK_BART_STATION_DEPARTURES = {
    "station": [
        {
            "name": "West Oakland",
            "abbr": "WOAK",
            "etd": [
                {
                    "destination": "Antioch",
                    "abbreviation": "ANTC",
                    "limited": "0",
                    "estimate": [
                        {
                            "minutes": "7",
                            "platform": "2",
                            "direction": "North",
                            "length": "10",
                            "color": "YELLOW",
                            "hexcolor": "#ffff33",
                            "bikeflag": "1",
                            "delay": "0"
                        },
                        {
                            "minutes": "22",
                            "platform": "2",
                            "direction": "North",
                            "length": "10",
                            "color": "YELLOW",
                            "hexcolor": "#ffff33",
                            "bikeflag": "1",
                            "delay": "0"
                        },
                    ]
                }
            ]
        }
    ]
}

MOCK_BART_ALL_DEPARTURES = {
    'station': [
        {
            "name": "Dublin/Pleasanton",
            "abbr": "DUBL",
            "etd": [
                {
                    "destination": "Daly City",
                    "abbreviation": "DALY",
                    "limited": "0",
                    "estimate": [
                        {
                            "minutes": "23",
                            "platform": "2",
                            "direction": "South",
                            "length": "10",
                            "color": "BLUE",
                            "hexcolor": "#0099cc",
                            "bikeflag": "1",
                            "delay": "0"
                        }
                    ]
                }
            ]
        },
        {
            "name": "West Oakland",
            "abbr": "WOAK",
            "etd": [
                {
                    "destination": "Antioch",
                    "abbreviation": "ANTC",
                    "limited": "0",
                    "estimate": [
                        {
                            "minutes": "3",
                            "platform": "2",
                            "direction": "North",
                            "length": "10",
                            "color": "YELLOW",
                            "hexcolor": "#ffff33",
                            "bikeflag": "1",
                            "delay": "0"
                        },
                    ]
                }
            ]
        }
    ]
}

MOCK_ACTRANSIT_STOP_DEPARTURES = {
    "bustime-response": {
        "prd": [
            {
                "tmstmp": "20211230 15:39",
                "typ": "A",
                "stpnm": "Mission Blvd & Central Blvd",
                "stpid": "51303",
                "vid": "1421",
                "dstp": 10993,
                "rt": "99",
                "rtdd": "99",
                "rtdir": "To Hayward BART",
                "des": "Hayward BART",
                # TODO make this relative
                "prdtm": "20211230 15:48",
                "tablockid": "99006",
                "tatripid": "7633993",
                "origtatripno": "8681894",
                "dly": False,
                "dyn": 0,
                "prdctdn": "9",
                "zone": "",
                "rid": "9919",
                "tripid": "2513020",
                "tripdyn": 0,
                "schdtm": "20211230 15:51",
                "geoid": "5282",
                "seq": 47,
                "psgld": "",
                "stst": 54000,
                "stsd": "2021-12-30"
            },
        ]
    }
}

MOCK_NEXTBUS_STOP_PREDICTION = {
    "predictions": [
        {
            "agencyTitle": "San Francisco Muni",
            "routeTitle": "38-Geary",
            "routeTag": "38",
            "stopTitle": "Market St & Montgomery St",
            "stopTag": "5684",
            "direction": {
                "title": "Outbound to V. A. Hospital",
                "prediction": {
                    # TODO make this relative
                    "epochTime": "1640921531578",
                    "seconds": "148",
                    "minutes": "2",
                    "isDeparture": "false",
                    "dirTag": "38___O_F10",
                    "vehicle": "6510",
                    "block": "3801",
                    "tripTag": "10341551"
                }
            },
        }
    ]
}


@pytest.fixture
def planner():
    client = TripPlanner('')
    yield client
    client.close()


def test_leg_bart(mocker, planner):
    mocker.patch('trip_planner.client.bart.station_list', return_value=MOCK_BART_STATION_LIST)
    mocker.patch('trip_planner.client.bart.station_departures', return_value=MOCK_BART_STATION_DEPARTURES)
    planner.leg_create('bart', 'woak')
    leg_list = planner.leg_list()
    assert len(leg_list) == 1
    assert leg_list[0]['stop_id'] == 'woak'
    assert leg_list[0]['stop_title'] == 'West Oakland'
    agency, departures = planner.leg_show(1)
    assert agency == 'bart'
    assert len(departures) == 1
    planner.leg_delete(1)

def test_leg_actransit(mocker, planner):
    mocker.patch('trip_planner.client.actransit.stop_predictions', return_value=MOCK_ACTRANSIT_STOP_DEPARTURES)
    planner.leg_create('actransit', '51303')
    leg_list = planner.leg_list()
    assert len(leg_list) == 1
    assert leg_list[0]['stop_id'] == '51303'
    agency, departures = planner.leg_show(1)
    assert agency == 'actransit'
    assert len(departures) > 0

def test_leg_nextbus(mocker, planner):
    mocker.patch('trip_planner.client.nextbus.stop_prediction', return_value=MOCK_NEXTBUS_STOP_PREDICTION)
    planner.leg_create('sf-muni', '15684')
    leg_list = planner.leg_list()
    assert len(leg_list) == 1
    assert leg_list[0]['stop_id'] == '15684'
    agency, departures = planner.leg_show(1)
    assert agency == 'sf-muni'
    assert len(departures) > 0

def test_trip(mocker, planner):
    mocker.patch('trip_planner.client.bart.station_list', return_value=MOCK_BART_STATION_LIST)
    mocker.patch('trip_planner.client.bart.station_departures', return_value=MOCK_BART_STATION_DEPARTURES)
    mocker.patch('trip_planner.client.actransit.stop_predictions', return_value=MOCK_ACTRANSIT_STOP_DEPARTURES)
    mocker.patch('trip_planner.client.nextbus.stop_prediction', return_value=MOCK_NEXTBUS_STOP_PREDICTION)
    planner.leg_create('bart', 'woak')
    planner.leg_create('actransit', '51303')
    planner.leg_create('sf-muni', '15684')

    planner.trip_create('testing', [1, 2, 3])

    trip_list = planner.trip_list()
    assert len(trip_list) == 1
    assert len(trip_list[0]['legs']) == 3

    mocker.patch('trip_planner.client.bart.station_departures', return_value=MOCK_BART_ALL_DEPARTURES)
    mocker.patch('trip_planner.client.nextbus.stop_multiple_predictions', return_value=MOCK_NEXTBUS_STOP_PREDICTION)
    planner.trip_show(1)
    planner.trip_delete(trip_list[0]['id'])


# --- error / edge-case tests ---

def test_leg_create_invalid_bart_station(mocker, planner):
    mocker.patch('trip_planner.client.bart.station_list', return_value=MOCK_BART_STATION_LIST)
    with pytest.raises(TripPlannerException):
        planner.leg_create('bart', 'invalid')


def test_leg_create_nextbus_transit_error(mocker, planner):
    mocker.patch(
        'trip_planner.client.nextbus.stop_prediction',
        side_effect=TransitException('bad stop'),
    )
    with pytest.raises(TripPlannerException):
        planner.leg_create('sf-muni', '99999')


def test_leg_show_not_found(planner):
    with pytest.raises(TripPlannerException):
        planner.leg_show(999)


def test_leg_show_bart_with_destinations(mocker, planner):
    mocker.patch('trip_planner.client.bart.station_list', return_value=MOCK_BART_STATION_LIST)
    mocker.patch('trip_planner.client.bart.station_departures', return_value=MOCK_BART_STATION_DEPARTURES)
    planner.leg_create('bart', 'woak', destinations=['antc'])
    agency, departures = planner.leg_show(1)
    assert agency == 'bart'
    assert len(departures) == 1


def test_leg_show_actransit_with_destinations(mocker, planner):
    mocker.patch('trip_planner.client.actransit.stop_predictions', return_value=MOCK_ACTRANSIT_STOP_DEPARTURES)
    planner.leg_create('actransit', '51303', destinations=['99'])
    agency, departures = planner.leg_show(1)
    assert agency == 'actransit'
    assert len(departures) == 1


def test_leg_delete_in_use(mocker, planner):
    mocker.patch('trip_planner.client.bart.station_list', return_value=MOCK_BART_STATION_LIST)
    planner.leg_create('bart', 'woak')
    planner.trip_create('test', [1])
    with pytest.raises(TripPlannerException):
        planner.leg_delete(1)


def test_trip_create_invalid_leg(planner):
    with pytest.raises(TripPlannerException):
        planner.trip_create('test', [999])


def test_trip_list_multiple_trips(mocker, planner):
    mocker.patch('trip_planner.client.bart.station_list', return_value=MOCK_BART_STATION_LIST)
    planner.leg_create('bart', 'woak')
    planner.trip_create('trip1', [1])
    planner.trip_create('trip2', [1])
    trips = planner.trip_list()
    assert len(trips) == 2


def test_trip_show_not_found(planner):
    with pytest.raises(TripPlannerException):
        planner.trip_show(999)


def test_trip_show_with_destinations(mocker, planner):
    mocker.patch('trip_planner.client.bart.station_list', return_value=MOCK_BART_STATION_LIST)
    # bart leg with destination 'daly' — WOAK only has ANTC, so the departure is filtered out
    # (covers destination collection loop and the abbreviation-mismatch continue branch)
    mocker.patch('trip_planner.client.bart.station_departures', return_value=MOCK_BART_ALL_DEPARTURES)
    # actransit leg with destination '99' (covers actransit destination collection loop)
    mocker.patch('trip_planner.client.actransit.stop_predictions', return_value=MOCK_ACTRANSIT_STOP_DEPARTURES)
    planner.leg_create('bart', 'woak', destinations=['daly'])
    planner.leg_create('actransit', '51303', destinations=['99'])
    planner.trip_create('test', [1, 2])
    result = planner.trip_show(1)
    assert 'bart' in result
    assert 'actransit' in result
