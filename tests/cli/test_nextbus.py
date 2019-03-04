import datetime
from io import StringIO

import mock

from transit.cli.nextbus import generate_args, NextbusCLI

from tests.utils import TestRunnerHelper

class TestBartCli(TestRunnerHelper):
    def test_agency_list(self):
        expected = '''+---------------------+-----------+------------+
|        Region       |    Tag    |   Title    |
+---------------------+-----------+------------+
| California-Northern | actransit | AC Transit |
|       Maryland      |  jhu-apl  |    APL     |
+---------------------+-----------+------------+
'''
        with mock.patch('transit.nextbus.agency_list') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = [
                    {
                        'tag': 'actransit',
                        'region': 'California-Northern',
                        'title': 'AC Transit'
                    },
                    {
                        'tag': 'jhu-apl',
                        'region': 'Maryland',
                        'title': 'APL'
                    },
                ]
                args = generate_args(['agency', 'list'])
                nextbus_cli = NextbusCLI(**args)
                nextbus_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_route_list(self):
        expected = '''+-----+---------------------------+
| Tag |           Title           |
+-----+---------------------------+
|  B  |             B             |
| BSD | Broadway Shuttle Weekdays |
+-----+---------------------------+
'''
        with mock.patch('transit.nextbus.route_list') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = [
                    {'title': 'B', 'tag': 'B'},
                    {'title': 'Broadway Shuttle Weekdays', 'tag': 'BSD'},
                ]
                args = generate_args(['route', 'list', 'sf-muni'])
                nextbus_cli = NextbusCLI(**args)
                nextbus_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_route_show(self):
        expected = '''{
    "latitude_max": 37.6707999,
    "latitude_min": 37.6308399,
    "longitude_max": -122.05466,
    "longitude_min": -122.1086899,
    "opposite_color": "000000",
    "tag": "22",
    "title": "22"
}
+------------+------------+---------+----------+----------------------+
|  Latitude  | Longitude  | Stop Id | Stop Tag |        Title         |
+------------+------------+---------+----------+----------------------+
|  37.66447  | -122.08751 |  55390  | 0801430  |    D St & Meek Av    |
| 37.6696299 | -122.08661 |  55911  | 0802060  | Hayward BART Station |
+------------+------------+---------+----------+----------------------+
'''
        with mock.patch('transit.nextbus.route_show') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = {
                    'opposite_color': '000000',
                    'longitude_max': -122.05466,
                    'stops': [
                        {
                            'stop_tag': '0801430',
                            'latitude': 37.66447,
                            'title': 'D St & Meek Av',
                            'stop_id': '55390',
                            'longitude': -122.08751
                        },
                        {
                            'stop_tag': '0802060',
                            'latitude': 37.6696299,
                            'title': 'Hayward BART Station',
                            'stop_id': '55911',
                            'longitude': -122.08661,
                        },
                    ],
                    'title': '22',
                    'latitude_max': 37.6707999,
                    'tag': '22',
                    'paths': [
                        [
                            {
                                'longitude': -122.09648,
                                'latitude': 37.63084
                            },
                            {
                                'longitude': -122.09651,
                                'latitude': 37.63089
                            },
                        ],
                        [
                            {
                                'longitude': -122.05683,
                                'latitude': 37.63456
                            },
                            {
                                'longitude': -122.05676,
                                'latitude': 37.63459
                            },
                        ]
                    ],
                    'latitude_min': 37.6308399,
                    'longitude_min': -122.1086899,
                    }

                args = generate_args(['route', 'show', 'sf-muni', 'J'])
                nextbus_cli = NextbusCLI(**args)
                nextbus_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_route_schedule(self):
        expected = '''Direction: Clockwis Service Class: wkd
+----------+----------+--------------------------+
|   Time   | Stop Tag |          Title           |
+----------+----------+--------------------------+
| 05:45:00 | 0802060  |   Hayward BART Station   |
| 05:54:00 | 9902130  | Mission Blvd & Harder Rd |
| 06:15:00 | 0802060  |   Hayward BART Station   |
+----------+----------+--------------------------+
'''
        with mock.patch('transit.nextbus.schedule_get') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = [
                    {
                        'direction': 'Clockwis',
                        'schedule_class': '1412WR',
                        'blocks': [
                            {
                                'block_id': '22001',
                                'stop_schedules': [
                                    {
                                        'stop_tag': '0802060',
                                        'time': datetime.datetime(1900, 1, 1, 5, 45),
                                        'epoch_time': 20700000,
                                        'title': 'Hayward BART Station'
                                    },
                                    {
                                        'stop_tag': '9902130',
                                        'time': datetime.datetime(1900, 1, 1, 5, 54),
                                        'epoch_time': 21240000,
                                        'title': 'Mission Blvd & Harder Rd'
                                    }
                                ]
                            },
                            {
                                'block_id': '22003',
                                'stop_schedules': [
                                    {
                                        'stop_tag': '0802060',
                                        'time': datetime.datetime(1900, 1, 1, 6, 15),
                                        'epoch_time': 22500000,
                                        'title': 'Hayward BART Station',
                                    },
                                ]
                            },
                        ],
                        'tag': '22',
                        'service_class': 'wkd',
                        'title': '22'
                    }
                ]
                args = generate_args(['route', 'schedule', 'sf-muni', 'J'])
                nextbus_cli = NextbusCLI(**args)
                nextbus_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_route_messages(self):
        expected = '''{
    "messages": [
        {
            "end_boundary": null,
            "end_boundary_epoch": null,
            "message_id": "16279",
            "priority": "Low",
            "send_to_buses": null,
            "start_boundary": null,
            "start_boundary_epoch": null,
            "text": [
                "Go to sfmta.com 4 Email/Text Alerts."
            ]
        }
    ],
    "tag": "all"
}
'''
        with mock.patch('transit.nextbus.route_messages') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = [
                    {
                        'tag': 'all',
                        'messages': [
                            {
                                'message_id': '16279',
                                'start_boundary_epoch': None,
                                'send_to_buses': None,
                                'end_boundary_epoch': None,
                                'start_boundary': None,
                                'text': [
                                    'Go to sfmta.com 4 Email/Text Alerts.'
                                ],
                                'end_boundary': None,
                                'priority': 'Low'
                            },
                        ]
                    }
                ]
                args = generate_args(['route', 'messages', 'sf-muni', 'J'])
                nextbus_cli = NextbusCLI(**args)
                nextbus_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_route_vehicle(self):
        expected = '''+------------+----------+------------+
| Vehicle Id | Latitude | Longitude  |
+------------+----------+------------+
|    1495    | 37.75263 | -122.38459 |
|    1538    | 37.75136 | -122.38427 |
+------------+----------+------------+
'''
        with mock.patch('transit.nextbus.vehicle_location') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = [
                    {
                        'speed_km_hr': 0,
                        'heading': '-4',
                        'latitude': 37.75263,
                        'seconds_since_last_report': 28,
                        'vehicle_id': '1495',
                        'predictable': False,
                        'route_tag': 'N',
                        'longitude': -122.38459
                    },
                    {
                        'speed_km_hr': 0,
                        'heading': '-4',
                        'latitude': 37.75136,
                        'seconds_since_last_report': 36,
                        'vehicle_id': '1538',
                        'predictable': False,
                        'route_tag': 'N',
                        'longitude': -122.38427
                    },
                ]
                args = generate_args(['route', 'vehicle', 'sf-muni', 'J', '12345'])
                nextbus_cli = NextbusCLI(**args)
                nextbus_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_stop_prediction(self):
        expected = '''Agency: AC Transit
+-------+----------------------------------+------------------+
| Route |            Direction             |   Predictions    |
+-------+----------------------------------+------------------+
|   22  | Counterclockwise to Hayward BART | 53:16 ; 01:01:36 |
+-------+----------------------------------+------------------+
'''
        with mock.patch('transit.nextbus.stop_prediction') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = [
                    {
                        'agency_title': 'AC Transit',
                        'messages': [
                            'Hey hey hey this is a message'
                        ],
                        'route_tag': '22',
                        'stop_title': 'Mission Blvd & Central Blvd',
                        'route_title': '22',
                        'directions': [
                            {
                                'title': 'Counterclockwise to Hayward BART',
                                'predictions': [
                                    {
                                        'seconds': 3196,
                                        'vehicle': '1216',
                                        'dir_tag': '22_25_1',
                                        'trip_tag': '3965673',
                                        'affected_by_layover': True,
                                        'minutes': 53,
                                        'epoch_time': 1424062084430,
                                        'is_departure': False,
                                        'block': '22001'
                                    },
                                    {
                                        'seconds': 3696,
                                        'vehicle': '1216',
                                        'dir_tag': '22_25_1',
                                        'trip_tag': '3965673',
                                        'affected_by_layover': True,
                                        'minutes': 53,
                                        'epoch_time': 1424062084430,
                                        'is_departure': False,
                                        'block': '22001'
                                    }
                                ]
                            }
                        ]
                    }
                ]
                args = generate_args(['stop', 'prediction', 'sf-muni', '1235'])
                nextbus_cli = NextbusCLI(**args)
                nextbus_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)
