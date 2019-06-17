from io import StringIO

import mock

from transit.cli.actransit import generate_args, ACTransitCLI

from tests.utils import TestRunnerHelper

class TestACTransitCli(TestRunnerHelper):
    def test_route_list(self):
        expected = '''+------+---------+-------------------------+
| Name | Routeid |       Description       |
+------+---------+-------------------------+
|  1   |    1    | International - E. 14th |
+------+---------+-------------------------+
'''
        with mock.patch('transit.actransit.route_list') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = [
                    {
                        "RouteId": "1",
                        "Name": "1",
                        "Description": "International - E. 14th"
                    },
                ]
                args = generate_args(['-k', 'foo', 'route', 'list'])
                bart_cli = ACTransitCLI(**args)
                bart_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_route_directions(self):
        expected = '''[
    "North",
    "South"
]
'''
        with mock.patch('transit.actransit.route_directions') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = [
                    'North',
                    'South',
                ]
                args = generate_args(['-k', 'foo', 'route', 'directions', '51A'])
                bart_cli = ACTransitCLI(**args)
                bart_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_route_trips(self):
        expected = '''+---------+---------------------+
|  Tripid |      Starttime      |
+---------+---------------------+
| 6783494 | 2000-01-01T05:01:00 |
+---------+---------------------+
'''
        with mock.patch('transit.actransit.route_trips') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = [
                    {
                        "StartTime": "2000-01-01T05:01:00",
                        "TripId": 6783494,
                    },
                ]
                args = generate_args(['-k', 'foo', 'route', 'trips', '51A',
                                      'Southbound'])
                bart_cli = ACTransitCLI(**args)
                bart_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_route_stops(self):
        expected = '''+--------+---------------------+------------+--------------+---------------+
| Stopid |         Name        |  Latitude  |  Longitude   | Scheduledtime |
+--------+---------------------+------------+--------------+---------------+
| 54327  | College Av:Miles Av | 37.8445417 | -122.2519663 |      None     |
+--------+---------------------+------------+--------------+---------------+
'''
        with mock.patch('transit.actransit.route_stops') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = [
                    {
                        "Longitude": -122.2519663,
                        "Name": "College Av:Miles Av",
                        "Latitude": 37.8445417,
                        "StopId": 54327,
                        "ScheduledTime": None
                    },
                ]
                args = generate_args(['-k', 'foo', 'route', 'stops', '51A', '1234'])
                bart_cli = ACTransitCLI(**args)
                bart_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_stop_predictions(self):
        expected = '''+-------+-------------------+--------------------------+---------------+
| Route |  Route direction  |        Stop title        |  Predictions  |
+-------+-------------------+--------------------------+---------------+
|  51A  | To Rockridge BART | Santa Clara Av + Park St | 00:25 ; 00:25 |
+-------+-------------------+--------------------------+---------------+
'''
        with mock.patch('transit.actransit.stop_predictions') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                with mock.patch('transit.cli.actransit.clean_pred_time') as mock_time:
                    mock_time.return_value = '00:25'
                    mock_method.return_value = [
                        {
                            "prdtm": 'foo',
                            "rtdir": "To Rockridge BART",
                            "rt": "51A",
                            "stpnm": "Santa Clara Av + Park St",
                            "tripid" : '1234',
                            'stpid' : '55511',
                        },
                        {
                            "prdtm": 'bar',
                            "rtdir": "To Rockridge BART",
                            "rt": "51A",
                            "stpnm": "Santa Clara Av + Park St",
                            "tripid" : '1234',
                            'stpid' : '55511',
                        }
                    ]
                    args = generate_args(['-k', 'foo', 'stop', 'predictions', '1234'])
                    bart_cli = ACTransitCLI(**args)
                    bart_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)

    def test_service_notices(self):
        expected = '''{
    "ImpactedRoutes": [
        "36",
        "51B",
        "52",
        "6",
        "604",
        "605",
        "79",
        "851 and F"
    ],
    "NoticeText": "Due to construction, lines 6, 36, 51B, 52, 79, 604",
    "PostDate": "2019-05-31T16:10:01",
    "Title": "Stops Closed Bancroft at Dana and Ellsworth",
    "Url": "http://actransit.org/stops-closed-bancroft-at-dana-and-ellsworth"
}
'''
        with mock.patch('transit.actransit.service_notices') as mock_method:
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                mock_method.return_value = [
                    {
                        "Url": "http://actransit.org/stops-closed-bancroft-at-dana-and-ellsworth",
                        "PostDate": "2019-05-31T16:10:01",
                        "NoticeText": "Due to construction, lines 6, 36, 51B, 52, 79, 604",
                        "Title": "Stops Closed Bancroft at Dana and Ellsworth",
                        "ImpactedRoutes": [
                            "36",
                            "51B",
                            "52",
                            "6",
                            "604",
                            "605",
                            "79",
                            "851 and F"
                        ]
                    },
                ]
                args = generate_args(['-k', 'foo', 'service', 'notices'])
                bart_cli = ACTransitCLI(**args)
                bart_cli.run_command()
        self.assertEqual(mock_out.getvalue(), expected)
