from io import StringIO

import mock

from trip_planner.cli.planner_script import generate_args, TripPlannerCLI

from tests.utils import TestRunnerHelper, temp_file

class TestPlannerCLI(TestRunnerHelper):
    def test_config(self):
        # Write data to config, make sure its read correctly
        with temp_file(suffix='.sql') as temp_db:
            with temp_file(suffix='.conf') as temp_config:
                with open(temp_config, 'w') as temp_config_writer:
                    temp_config_writer.write('[keys]\nactransit_api_key=foo\nbart_api_key=bar\n')
                args = generate_args(['-d', temp_db, '-c', temp_config, 'leg', 'list'])
                trip_planner_cli = TripPlannerCLI(**args)
                print(trip_planner_cli.kwargs)
        self.assertEqual(trip_planner_cli.kwargs['actransit_api_key'], 'foo')
        self.assertEqual(trip_planner_cli.kwargs['bart_api_key'], 'bar')


    def test_empty_config(self):
        with temp_file(suffix='.sql') as temp_db:
            with temp_file(suffix='.conf') as temp_config:
                with open(temp_config, 'w') as temp_config_writer:
                    temp_config_writer.write('\n')
                args = generate_args(['-d', temp_db, '-c', temp_config, 'leg', 'list'])
                trip_planner_cli = TripPlannerCLI(**args)
                print(trip_planner_cli.kwargs)
        self.assertEqual(trip_planner_cli.kwargs['actransit_api_key'], None)
        self.assertEqual(trip_planner_cli.kwargs['bart_api_key'], None)



    def test_leg_create(self):
        expected = '''Leg created: 1
{
    "agency": "bart",
    "includes": [
        "hayw"
    ],
    "stop_id": "rich",
    "stop_tag": null,
    "stop_title": "Richmond"
}
'''
        with temp_file(suffix='.sql') as temp_db:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                with mock.patch('transit.bart.station_info') as mock_method_one:
                    mock_method_one.return_value = {
                        'north_routes' : [
                            2
                        ],
                        'south_routes' : [],
                    }
                    with mock.patch('transit.bart.route_info') as mock_method_two:
                        mock_method_two.return_value = {
                            'destination' : 'hayw'
                        }
                        args = generate_args(['-d', temp_db, 'leg', 'create', 'bart', 'rich'])
                        trip_planner_cli = TripPlannerCLI(**args)
                        trip_planner_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_leg_list(self):
        expected = '''Leg created: 1
{
    "agency": "bart",
    "includes": [
        "hayw"
    ],
    "stop_id": "rich",
    "stop_tag": null,
    "stop_title": "Richmond"
}
+----+--------+------------+----------+--------------+
| Id | Agency | Stop Title | Stop Tag | Destinations |
+----+--------+------------+----------+--------------+
| 1  |  bart  |  Richmond  |   None   |     hayw     |
+----+--------+------------+----------+--------------+
'''
        with temp_file(suffix='.sql') as temp_db:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                # First create leg
                with mock.patch('transit.bart.station_info') as mock_method_one:
                    mock_method_one.return_value = {
                        'north_routes' : [
                            2
                        ],
                        'south_routes' : [],
                    }
                    with mock.patch('transit.bart.route_info') as mock_method_two:
                        mock_method_two.return_value = {
                            'destination' : 'hayw'
                        }
                        args = generate_args(['-d', temp_db, 'leg', 'create', 'bart', 'rich'])
                        trip_planner_cli = TripPlannerCLI(**args)
                        trip_planner_cli.run_command()

                # Then list legs
                args = generate_args(['-d', temp_db, 'leg', 'list'])
                trip_planner_cli = TripPlannerCLI(**args)
                trip_planner_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_leg_show_bart(self):
        expected = '''Leg created: 1
{
    "agency": "bart",
    "includes": [
        "warm"
    ],
    "stop_id": "rich",
    "stop_tag": null,
    "stop_title": "Richmond"
}
Agency: bart
+----------+--------------+-----------------------+
| Station  |  Direction   | Estimates ( minutes ) |
+----------+--------------+-----------------------+
| Richmond | Warm Springs |      9 ; 24 ; 39      |
+----------+--------------+-----------------------+
'''
        with temp_file(suffix='.sql') as temp_db:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                # First create leg
                with mock.patch('transit.bart.station_info') as mock_method_one:
                    mock_method_one.return_value = {
                        'north_routes' : [
                            2
                        ],
                        'south_routes' : [],
                    }
                    with mock.patch('transit.bart.route_info') as mock_method_two:
                        mock_method_two.return_value = {
                            'destination' : 'warm'
                        }
                        args = generate_args(['-d', temp_db, 'leg', 'create', 'bart', 'rich'])
                        trip_planner_cli = TripPlannerCLI(**args)
                        trip_planner_cli.run_command()

                # Then show leg
                with mock.patch('transit.bart.station_departures') as mock_method:
                    mock_method.return_value = [
                        {
                            'directions': [
                                {
                                    'estimates': [
                                        {
                                            'minutes': 9,
                                        },
                                        {
                                            'minutes': 24,
                                        },
                                        {
                                            'minutes': 39,
                                        }
                                    ],
                                    'name': 'Warm Springs',
                                    'abbreviation': 'warm'
                                }
                            ],
                            'name': 'Richmond',
                            'abbreviation': 'rich',
                        }
                    ]
                    args = generate_args(['-d', temp_db, 'leg', 'show', '1'])
                    trip_planner_cli = TripPlannerCLI(**args)
                    trip_planner_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_leg_show_nextbus(self):
        expected = '''Leg created: 1
{
    "agency": "sf-muni",
    "includes": [
        "38"
    ],
    "stop_id": "17620",
    "stop_tag": "7620",
    "stop_title": "Main St & Howard St"
}
Agency: San Francisco Muni
+---------------------+----------+----------------------------+-------------+
|         Stop        |  Route   |         Direction          | Predictions |
+---------------------+----------+----------------------------+-------------+
| Main St & Howard St | 38-Geary | Outbound to V. A. Hospital |    13:26    |
+---------------------+----------+----------------------------+-------------+
'''
        with temp_file(suffix='.sql') as temp_db:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                # First create leg
                with mock.patch('transit.nextbus.stop_prediction') as mock_method_one:
                    mock_method_one.return_value = [
                        {
                            'route_tag' : '38'
                        }
                    ]
                    with mock.patch('transit.nextbus.route_show') as mock_method_two:
                        mock_method_two.return_value = {
                            'stops' : [
                                {
                                    'stop_id' : '17620',
                                    'stop_tag' : '7620',
                                    'title' : 'Main St & Howard St'
                                }
                            ]
                        }
                        args = generate_args(['-d', temp_db, 'leg', 'create', 'sf-muni', '17620'])
                        trip_planner_cli = TripPlannerCLI(**args)
                        trip_planner_cli.run_command()
                # Now show leg
                with mock.patch('transit.nextbus.stop_prediction') as mock_method:
                    mock_method.return_value = [
                        {
                            'route_tag': '38',
                            'stop_title': 'Main St & Howard St',
                            'messages': [
                                '5/5R, 7, 25, 38/38R using Temp Transbay terminal at Howard/Main'
                            ],
                            'route_title': '38-Geary',
                            'directions': [
                                {
                                    'predictions': [
                                        {
                                            'seconds': 806,
                                        },
                                    ],
                                    'title': 'Outbound to V. A. Hospital'
                                }
                            ],
                            'agency_title': 'San Francisco Muni'
                        }
                    ]
                    args = generate_args(['-d', temp_db, 'leg', 'show', '1'])
                    trip_planner_cli = TripPlannerCLI(**args)
                    trip_planner_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)


    def test_leg_delete(self):
        expected = '''Leg created: 1
{
    "agency": "bart",
    "includes": [
        "hayw"
    ],
    "stop_id": "rich",
    "stop_tag": null,
    "stop_title": "Richmond"
}
Legs deleted: 1
'''
        with temp_file(suffix='.sql') as temp_db:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                # First make leg
                with mock.patch('transit.bart.station_info') as mock_method_one:
                    mock_method_one.return_value = {
                        'north_routes' : [
                            2
                        ],
                        'south_routes' : [],
                    }
                    with mock.patch('transit.bart.route_info') as mock_method_two:
                        mock_method_two.return_value = {
                            'destination' : 'hayw'
                        }
                        args = generate_args(['-d', temp_db, 'leg', 'create', 'bart', 'rich'])
                        trip_planner_cli = TripPlannerCLI(**args)
                        trip_planner_cli.run_command()
                # Now delete
                args = generate_args(['-d', temp_db, 'leg', 'delete', '1'])
                trip_planner_cli = TripPlannerCLI(**args)
                trip_planner_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_trip_create(self):
        expected = '''Leg created: 1
{
    "agency": "bart",
    "includes": [
        "hayw"
    ],
    "stop_id": "rich",
    "stop_tag": null,
    "stop_title": "Richmond"
}
Trip created: 1
{
    "legs": [
        1
    ],
    "name": "foo"
}
'''
        with temp_file(suffix='.sql') as temp_db:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                # First make leg
                with mock.patch('transit.bart.station_info') as mock_method_one:
                    mock_method_one.return_value = {
                        'north_routes' : [
                            2
                        ],
                        'south_routes' : [],
                    }
                    with mock.patch('transit.bart.route_info') as mock_method_two:
                        mock_method_two.return_value = {
                            'destination' : 'hayw'
                        }
                        args = generate_args(['-d', temp_db, 'leg', 'create', 'bart', 'rich'])
                        trip_planner_cli = TripPlannerCLI(**args)
                        trip_planner_cli.run_command()
                # Now create trip
                args = generate_args(['-d', temp_db, 'trip', 'create', 'foo', '1'])
                trip_planner_cli = TripPlannerCLI(**args)
                trip_planner_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_trip_list(self):
        expected = '''Leg created: 1
{
    "agency": "bart",
    "includes": [
        "hayw"
    ],
    "stop_id": "rich",
    "stop_tag": null,
    "stop_title": "Richmond"
}
Trip created: 1
{
    "legs": [
        1
    ],
    "name": "foo"
}
+----+------+------+
| Id | Name | Legs |
+----+------+------+
| 1  | foo  |  1   |
+----+------+------+
'''
        with temp_file(suffix='.sql') as temp_db:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                # First make leg
                with mock.patch('transit.bart.station_info') as mock_method_one:
                    mock_method_one.return_value = {
                        'north_routes' : [
                            2
                        ],
                        'south_routes' : [],
                    }
                    with mock.patch('transit.bart.route_info') as mock_method_two:
                        mock_method_two.return_value = {
                            'destination' : 'hayw'
                        }
                        args = generate_args(['-d', temp_db, 'leg', 'create', 'bart', 'rich'])
                        trip_planner_cli = TripPlannerCLI(**args)
                        trip_planner_cli.run_command()
                # Now create trip
                args = generate_args(['-d', temp_db, 'trip', 'create', 'foo', '1'])
                trip_planner_cli = TripPlannerCLI(**args)
                trip_planner_cli.run_command()
                # Now list trips
                args = generate_args(['-d', temp_db, 'trip', 'list'])
                trip_planner_cli = TripPlannerCLI(**args)
                trip_planner_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_trip_delete(self):
        expected = '''Leg created: 1
{
    "agency": "bart",
    "includes": [
        "hayw"
    ],
    "stop_id": "rich",
    "stop_tag": null,
    "stop_title": "Richmond"
}
Trip created: 1
{
    "legs": [
        1
    ],
    "name": "foo"
}
Trips deleted: 1
'''
        with temp_file(suffix='.sql') as temp_db:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                # First make leg
                with mock.patch('transit.bart.station_info') as mock_method_one:
                    mock_method_one.return_value = {
                        'north_routes' : [
                            2
                        ],
                        'south_routes' : [],
                    }
                    with mock.patch('transit.bart.route_info') as mock_method_two:
                        mock_method_two.return_value = {
                            'destination' : 'hayw'
                        }
                        args = generate_args(['-d', temp_db, 'leg', 'create', 'bart', 'rich'])
                        trip_planner_cli = TripPlannerCLI(**args)
                        trip_planner_cli.run_command()
                # Now create trip
                args = generate_args(['-d', temp_db, 'trip', 'create', 'foo', '1'])
                trip_planner_cli = TripPlannerCLI(**args)
                trip_planner_cli.run_command()
                # Now delete trip
                args = generate_args(['-d', temp_db, 'trip', 'delete', '1'])
                trip_planner_cli = TripPlannerCLI(**args)
                trip_planner_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_trip_show(self):
        # TODO Disabled due to new functionality
        return True
        expected = '''Leg created: 1
{
    "agency": "sf-muni",
    "includes": [
        "38"
    ],
    "stop_id": "17620",
    "stop_tag": "7620",
    "stop_title": "Main St & Howard St"
}
Leg created: 2
{
    "agency": "bart",
    "includes": [
        "warm"
    ],
    "stop_id": "rich",
    "stop_tag": null,
    "stop_title": "Richmond"
}
Trip created: 1
{
    "legs": [
        1,
        2
    ],
    "name": "foo"
}
Agency: bart
+----------+--------------+-----------------------+
| Station  |  Direction   | Estimates ( minutes ) |
+----------+--------------+-----------------------+
| Richmond | Warm Springs |      9 ; 24 ; 39      |
+----------+--------------+-----------------------+
Agency: San Francisco Muni
+---------------------+----------+----------------------------+-------------+
|         Stop        |  Route   |         Direction          | Predictions |
+---------------------+----------+----------------------------+-------------+
| Main St & Howard St | 38-Geary | Outbound to V. A. Hospital |    13:26    |
+---------------------+----------+----------------------------+-------------+
'''
        with temp_file(suffix='.sql') as temp_db:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                # First create leg for nextbus
                with mock.patch('transit.nextbus.stop_prediction') as mock_method_one:
                    mock_method_one.return_value = [
                        {
                            'route_tag' : '38'
                        }
                    ]
                    with mock.patch('transit.nextbus.route_show') as mock_method_two:
                        mock_method_two.return_value = {
                            'stops' : [
                                {
                                    'stop_id' : '17620',
                                    'stop_tag' : '7620',
                                    'title' : 'Main St & Howard St'
                                }
                            ]
                        }
                        args = generate_args(['-d', temp_db, 'leg', 'create', 'sf-muni', '17620'])
                        trip_planner_cli = TripPlannerCLI(**args)
                        trip_planner_cli.run_command()
                # Next create leg for bart
                with mock.patch('transit.bart.station_info') as mock_method_one:
                    mock_method_one.return_value = {
                        'north_routes' : [
                            2
                        ],
                        'south_routes' : [],
                    }
                    with mock.patch('transit.bart.route_info') as mock_method_two:
                        mock_method_two.return_value = {
                            'destination' : 'warm'
                        }
                        args = generate_args(['-d', temp_db, 'leg', 'create', 'bart', 'rich'])
                        trip_planner_cli = TripPlannerCLI(**args)
                        trip_planner_cli.run_command()
                # Now create trip
                args = generate_args(['-d', temp_db, 'trip', 'create', 'foo', '1', '2'])
                trip_planner_cli = TripPlannerCLI(**args)
                trip_planner_cli.run_command()

                # Now show trip
                with mock.patch('transit.bart.station_multiple_departures') as mock_method_one:
                    mock_method_one.return_value = [
                        {
                            'directions': [
                                {
                                    'estimates': [
                                        {
                                            'minutes': 9,
                                        },
                                        {
                                            'minutes': 24,
                                        },
                                        {
                                            'minutes': 39,
                                        }
                                    ],
                                    'name': 'Warm Springs',
                                    'abbreviation': 'warm'
                                }
                            ],
                            'name': 'Richmond',
                            'abbreviation': 'rich',
                        }
                    ]
                    with mock.patch('transit.nextbus.stop_multiple_predictions') as mock_method_two:
                        mock_method_two.return_value = [
                            {
                                'route_tag': '38',
                                'stop_title': 'Main St & Howard St',
                                'messages': [
                                    '5/5R, 7, 25, 38/38R using Temp '\
                                    'Transbay terminal at Howard/Main'
                                ],
                                'route_title': '38-Geary',
                                'directions': [
                                    {
                                        'predictions': [
                                            {
                                                'seconds': 806,
                                            },
                                        ],
                                        'title': 'Outbound to V. A. Hospital'
                                    }
                                ],
                                'agency_title': 'San Francisco Muni'
                            }
                        ]
                        args = generate_args(['-d', temp_db, 'trip', 'show', '1'])
                        trip_planner_cli = TripPlannerCLI(**args)
                        trip_planner_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)
