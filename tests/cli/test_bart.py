import datetime
from io import StringIO

import mock

from transit.cli.bart import generate_args, BartCLI

from tests.utils import TestRunnerHelper

class TestBartCli(TestRunnerHelper):
    def test_service_advisory(self):
        expected = '''{
    "description": "BART is running round-the-clock service duringthe labor day weekend bay bridge closure. More info at www.bart.gov or (510) 465-2278.",
    "expires": "2037-12-31 23-59-00",
    "id": 112978,
    "posted": "2013-08-28 22-44-00",
    "station": "bart",
    "type": "delay"
}
'''
        with mock.patch('transit.bart.service_advisory') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = [
                    {
                        'station': 'bart',
                        'expires': datetime.datetime(2037, 12, 31, 23, 59),
                        'id': 112978,
                        'posted': datetime.datetime(2013, 8, 28, 22, 44),
                        'description': 'BART is running round-the-clock service during'\
                                       'the labor day weekend bay bridge closure. More info'\
                                       ' at www.bart.gov or (510) 465-2278.',
                        'type': 'delay'
                    }
                ]
                args = generate_args(['service', 'advisory'])
                bart_cli = BartCLI(**args)
                bart_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_train_count(self):
        with mock.patch('transit.bart.train_count') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = 5
                args = generate_args(['service', 'train-count'])
                bart_cli = BartCLI(**args)
                bart_cli.run_command()
        self.assertEqual(mock_out.getvalue(), '5\n')

    def test_elevator_status(self):
        expected = '''{
    "description": "There are two elevators out of service at this time:  Daly City Both Tunnel Elevators.  Thank you.",
    "expires": null,
    "id": 132264,
    "posted": "2015-06-30 15-56-00",
    "station": "bart",
    "type": "elevator"
}
'''
        with mock.patch('transit.bart.elevator_status') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = {
                    'description': 'There are two elevators out of service at this' \
                                   ' time:  Daly City Both Tunnel Elevators.  Thank you.',
                    'expires': None,
                    'id': 132264,
                    'posted': datetime.datetime(2015, 6, 30, 15, 56),
                    'station': 'bart',
                    'type': 'elevator'}
                args = generate_args(['service', 'elevator-status'])
                bart_cli = BartCLI(**args)
                bart_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_route_list(self):
        expected = '''Schedule Number:34
+--------------+---------+-------------------------------------+--------+
| Abbreviation |  Color  |                 Name                | Number |
+--------------+---------+-------------------------------------+--------+
|  pitt-sfia   | #ffff33 | Pittsburg/Bay Point - SFIA/Millbrae |   1    |
|  daly-dubl   | #0099cc |    Daly City - Dublin/Pleasanton    |   12   |
+--------------+---------+-------------------------------------+--------+
'''
        with mock.patch('transit.bart.route_list') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = {
                    'schedule_number': 34,
                    'routes': [
                        {
                            'abbreviation': 'pitt-sfia',
                            'name': 'Pittsburg/Bay Point - SFIA/Millbrae',
                            'color': '#ffff33',
                            'number': 1
                        },
                        {
                            'abbreviation': 'daly-dubl',
                            'name': 'Daly City - Dublin/Pleasanton',
                            'color': '#0099cc',
                            'number': 12
                        },
                    ]
                }
                args = generate_args(['route', 'list'])
                bart_cli = BartCLI(**args)
                bart_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_route_info(self):
        expected = '''{
    "abbreviation": "rich-frmt",
    "color": "#ff9933",
    "destination": "frmt",
    "holidays": true,
    "name": "Richmond - Fremont",
    "number": 4,
    "number_of_stations": 18,
    "origin": "rich",
    "stations": [
        "rich",
        "deln"
    ]
}
'''
        with mock.patch('transit.bart.route_info') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = {
                    'number_of_stations': 18,
                    'destination': 'frmt',
                    'name': 'Richmond - Fremont',
                    'color': '#ff9933',
                    'origin': 'rich',
                    'abbreviation': 'rich-frmt',
                    'stations': [
                        'rich',
                        'deln',
                    ],
                    'number': 4,
                    'holidays': True
                }
                args = generate_args(['route', 'info', '4'])
                bart_cli = BartCLI(**args)
                bart_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_station_list(self):
        expected = '''+--------------+---------------------+
| Abbreviation |         Name        |
+--------------+---------------------+
|     cast     |    Castro Valley    |
|     pitt     | Pittsburg/Bay Point |
+--------------+---------------------+
'''
        with mock.patch('transit.bart.station_list') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = {
                    'cast': 'Castro Valley',
                    'pitt': 'Pittsburg/Bay Point',
                }
                args = generate_args(['station', 'list'])
                bart_cli = BartCLI(**args)
                bart_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_station_info(self):
        expected = '''{
    "abbreviation": "hayw",
    "address": "699 'B' Street",
    "attraction": "attractions",
    "city": "Hayward",
    "county": "alameda",
    "cross_street": "Nearby Cross: Montgomery St.",
    "food": "food",
    "gtfs_latitude": 37.670399,
    "gtfs_longitude": -122.087967,
    "intro": "intro",
    "link": null,
    "name": "Hayward",
    "north_platforms": [
        2
    ],
    "north_routes": [
        3,
        5
    ],
    "platform_info": "Always check destination signs and listen for departure announcements.",
    "shopping": "shopping",
    "south_platforms": [
        1
    ],
    "south_routes": [
        4,
        6
    ],
    "state": "CA",
    "zipcode": 94541
}
'''
        with mock.patch('transit.bart.station_info') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = {
                    'zipcode': 94541,
                    'south_routes': [
                        4,
                        6
                    ],
                    'cross_street': 'Nearby Cross: Montgomery St.',
                    'abbreviation': 'hayw',
                    'state': 'CA',
                    'food': 'food',
                    'address': "699 'B' Street",
                    'city': 'Hayward',
                    'gtfs_latitude': 37.670399,
                    'attraction': 'attractions',
                    'gtfs_longitude': -122.087967,
                    'south_platforms': [
                        1
                    ],
                    'platform_info': 'Always check destination signs and listen '
                                     'for departure announcements.',
                    'county': 'alameda',
                    'north_routes': [
                        3,
                        5
                    ],
                    'link': None,
                    'north_platforms': [
                        2
                    ],
                    'name': 'Hayward',
                    'intro': 'intro',
                    'shopping': 'shopping',
                }
                args = generate_args(['station', 'info', 'dubl'])
                bart_cli = BartCLI(**args)
                bart_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_station_departures(self):
        expected = '''+----------+-----------+-----------------------+
| Station  | Direction | Estimates ( minutes ) |
+----------+-----------+-----------------------+
| Richmond |  Fremont  |         1 ; 18        |
+----------+-----------+-----------------------+
'''
        with mock.patch('transit.bart.station_departures') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = [
                    {
                        'abbreviation': 'rich',
                        'name': 'Richmond',
                        'directions': [
                            {
                                'abbreviation': 'frmt',
                                'estimates': [
                                    {
                                        'length': 6,
                                        'direction': 'south',
                                        'minutes': 1,
                                        'bike_flag': False,
                                        'platform': 2,
                                        'color': 'orange'
                                    },
                                    {
                                        'length': 6,
                                        'direction': 'south',
                                        'minutes': 18,
                                        'bike_flag': False,
                                        'platform': 2,
                                        'color': 'orange'
                                    },
                                ],
                                'name': 'Fremont',
                            },
                        ]
                    }
                ]
                args = generate_args(['station', 'departures', 'rich'])
                bart_cli = BartCLI(**args)
                bart_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_station_access(self):
        expected = '''{
    "abbreviation": "12th",
    "bike_flag": false,
    "destinations": "destination info",
    "entering": "entering message",
    "exiting": "exiting message",
    "link": null,
    "locker_flag": false,
    "lockers": "lockers message",
    "name": "12th St. Oakland City Center",
    "parking": "parking message",
    "parking_flag": false,
    "transit_info": "transit info"
}
'''
        with mock.patch('transit.bart.station_access') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = {
                    'exiting': 'exiting message',
                    'link': None,
                    'destinations': 'destination info',
                    'transit_info' : 'transit info',
                    'bike_flag': False,
                    'abbreviation': '12th',
                    'name': '12th St. Oakland City Center',
                    'lockers': 'lockers message',
                    'parking' : 'parking message',
                    'entering' : 'entering message',
                    'locker_flag': False,
                    'parking_flag': False
                }
                args = generate_args(['station', 'access', 'rich'])
                bart_cli = BartCLI(**args)
                bart_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_station_schedule(self):
        expected = '''Station Name: 12th St. Oakland City Center
+------+-------------+------------------+-----------+
| Line | Origin Time | Destination Time | Bike Flag |
+------+-------------+------------------+-----------+
|  7   |   04:36:00  |     05:21:00     |    True   |
+------+-------------+------------------+-----------+
'''
        with mock.patch('transit.bart.station_schedule') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = {
                    'schedule_times' : [
                        {
                            'origin_time': datetime.datetime(2019, 5, 6, 4, 36),
                            'line': 7,
                            'destination_time': datetime.datetime(2019, 5, 6, 5, 21),
                            'head_station': 'mlbr',
                            'train_index': 1,
                            'bike_flag': True
                        }
                    ],
                    'name' : '12th St. Oakland City Center',
                    'abbreviation' : '12th',
                }
                args = generate_args(['station', 'schedule', '12th'])
                bart_cli = BartCLI(**args)
                bart_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_schedule_list(self):
        expected = '''+----+----------------+
| Id | Effective Date |
+----+----------------+
| 34 |   2014-01-01   |
| 35 |   2014-11-22   |
+----+----------------+
'''
        with mock.patch('transit.bart.schedule_list') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = [
                    {
                        'effective_date': datetime.datetime(2014, 1, 1, 13, 0),
                        'id': 34
                    },
                    {
                        'effective_date': datetime.datetime(2014, 11, 22, 13, 0),
                        'id': 35
                    }
                ]
                args = generate_args(['schedule', 'list'])
                bart_cli = BartCLI(**args)
                bart_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_schedule_fare(self):
        expected = '''{
    "clipper": 1.2,
    "destination": "embr",
    "discount": 1.2,
    "fare": 3.3,
    "origin": "12th",
    "schedule_number": 35
}
'''
        with mock.patch('transit.bart.schedule_fare') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = {
                    'destination': 'embr',
                    'clipper': 1.2,
                    'schedule_number': 35,
                    'origin': '12th',
                    'discount': 1.2,
                    'fare': 3.3
                }
                args = generate_args(['schedule', 'fare', '12th', 'embr'])
                bart_cli = BartCLI(**args)
                bart_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)
