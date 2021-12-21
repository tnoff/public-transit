from trip_planner.client import TripPlanner

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

def test_leg_bart(mocker):
    mocker.patch('trip_planner.client.bart.station_list', return_value=MOCK_BART_STATION_LIST)
    mocker.patch('trip_planner.client.bart.station_departures', return_value=MOCK_BART_STATION_DEPARTURES)
    client = TripPlanner('')
    client.leg_create('bart', 'woak')
    leg_list = client.leg_list()
    assert len(leg_list) == 1
    assert leg_list[0]['stop_id'] == 'woak'
    assert leg_list[0]['stop_title'] == 'West Oakland'
    agency, departures = client.leg_show(1)
    assert agency == 'bart'
    assert len(departures) == 1
    client.leg_delete(1)

def test_leg_actransit(mocker):
    mocker.patch('trip_planner.client.actransit.stop_predictions', return_value=MOCK_ACTRANSIT_STOP_DEPARTURES)
    client = TripPlanner('')
    client.leg_create('actransit', '51303')
    leg_list = client.leg_list()
    assert len(leg_list) == 1
    assert leg_list[0]['stop_id'] == '51303'
    agency, departures = client.leg_show(1)
    assert agency == 'actransit'
    assert len(departures) > 0

def test_leg_nextbus(mocker):
    mocker.patch('trip_planner.client.nextbus.stop_prediction', return_value=MOCK_NEXTBUS_STOP_PREDICTION)
    client = TripPlanner('')
    client.leg_create('sf-muni', '15684')
    leg_list = client.leg_list()
    assert len(leg_list) == 1
    assert leg_list[0]['stop_id'] == '15684'
    agency, departures = client.leg_show(1)
    assert agency == 'sf-muni'
    assert len(departures) > 0

def test_trip(mocker):
    mocker.patch('trip_planner.client.bart.station_list', return_value=MOCK_BART_STATION_LIST)
    mocker.patch('trip_planner.client.bart.station_departures', return_value=MOCK_BART_STATION_DEPARTURES)
    mocker.patch('trip_planner.client.actransit.stop_predictions', return_value=MOCK_ACTRANSIT_STOP_DEPARTURES)
    mocker.patch('trip_planner.client.nextbus.stop_prediction', return_value=MOCK_NEXTBUS_STOP_PREDICTION)
    client = TripPlanner('')
    client.leg_create('bart', 'woak')
    client.leg_create('actransit', '51303')
    client.leg_create('sf-muni', '15684')

    client.trip_create('testing', [1, 2, 3])

    trip_list = client.trip_list()
    assert len(trip_list) == 1
    assert len(trip_list[0]['legs']) == 3

    mocker.patch('trip_planner.client.bart.station_departures', return_value=MOCK_BART_ALL_DEPARTURES)
    mocker.patch('trip_planner.client.nextbus.stop_multiple_predictions', return_value=MOCK_NEXTBUS_STOP_PREDICTION)
    result = client.trip_show(1)
    client.trip_delete(trip_list[0]['id'])