from transit.cli.bart import generate_args
from transit.exceptions import CLIException
from transit.modules.bart.settings import DATE_REGEX, DIRECTION_REGEX, STATION_REGEX

from tests.utils import TestRunnerHelper

class TestBartArgs(TestRunnerHelper):
    def test_no_args(self):
        '''
        Test basic command args throw proper errors
        '''
        with self.assertRaises(CLIException) as error:
            generate_args([''])
        self.check_error_message(error, "argument command: invalid choice: " \
                                        "'' (choose from 'service', 'route', " \
                                        "'station', 'schedule')")
        with self.assertRaises(CLIException) as error:
            generate_args([])
        self.check_error_message(error, "Error: No command arg present")

    def test_global_args(self):
        '''
        Test global args
        '''

        with self.assertRaises(CLIException) as error:
            generate_args(['-k'])
        self.check_error_message(error, "argument -k/--api-key: expected one argument")

        args = generate_args(['-k', 'foo', 'service', 'advisory'])
        self.assert_dictionary(args, {
            'command' : 'service',
            'subcommand' : 'advisory',
            'api_key' : 'foo',
        })

        args = generate_args(['--api-key', 'foo', 'service', 'advisory'])
        self.assert_dictionary(args, {
            'command' : 'service',
            'subcommand' : 'advisory',
            'api_key' : 'foo',
        })


    def test_service_args(self):
        '''
        Test service commands
        '''
        # Basic commands
        with self.assertRaises(CLIException) as error:
            generate_args(['service'])
        self.check_error_message(error, "Error: No sub-command arg present")

        with self.assertRaises(CLIException) as error:
            generate_args(['service', ''])
        self.check_error_message(error, "argument subcommand: invalid choice: "\
                                        "'' (choose from 'advisory', "\
                                        "'train-count', 'elevator-status')")
        # Each subcommand
        args = generate_args(['service', 'advisory'])
        self.assert_dictionary(args, {
            'command' : 'service',
            'subcommand' : 'advisory',
            'api_key' : None,
        })
        args = generate_args(['service', 'train-count'])
        self.assert_dictionary(args, {
            'command' : 'service',
            'subcommand' : 'train-count',
            'api_key' : None,
        })
        args = generate_args(['service', 'elevator-status'])
        self.assert_dictionary(args, {
            'command' : 'service',
            'subcommand' : 'elevator-status',
            'api_key' : None,
        })

    def test_route_args(self):
        '''
        Test route args
        '''
        # Basic commands
        with self.assertRaises(CLIException) as error:
            generate_args(['route'])
        self.check_error_message(error, "Error: No sub-command arg present")

        with self.assertRaises(CLIException) as error:
            generate_args(['route', ''])
        self.check_error_message(error, "argument subcommand: invalid choice: "\
                                        "'' (choose from 'list', 'info')")
        # List commands
        args = generate_args(['route', 'list'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'list',
            'schedule' : None,
            'date' : None,
            'api_key' : None,
        })
        args = generate_args(['route', 'list', '--schedule', '2'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'list',
            'schedule' : 2,
            'date' : None,
            'api_key' : None,
        })
        with self.assertRaises(CLIException) as error:
            generate_args(['route', 'list', '--schedule', 'foo'])
        self.check_error_message(error, "argument --schedule: invalid int value: 'foo'")
        args = generate_args(['route', 'list', '--date', '01/01/2019'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'list',
            'schedule' : None,
            'date' : '01/01/2019',
            'api_key' : None,
        })
        with self.assertRaises(CLIException) as error:
            generate_args(['route', 'list', '--date', 'derp'])
        self.check_error_message(error,
                                 "argument --date: String:derp does "\
                                 "not match regex:%s" % DATE_REGEX)
        args = generate_args(['route', 'list', '--schedule', '2', '--date', '01/01/2019'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'list',
            'schedule' : 2,
            'date' : '01/01/2019',
            'api_key' : None,
        })
        # Route info
        with self.assertRaises(CLIException) as error:
            generate_args(['route', 'info'])
        self.check_error_message(error, "the following arguments are required: route_number")

        with self.assertRaises(CLIException) as error:
            generate_args(['route', 'info', 'derp'])
        self.check_error_message(error, "argument route_number: invalid int value: 'derp'")
        args = generate_args(['route', 'info', '99'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'info',
            'route_number' : 99,
            'schedule' : None,
            'date' : None,
            'api_key' : None,
        })
        args = generate_args(['route', 'info', '99', '--schedule', '2'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'info',
            'route_number' : 99,
            'schedule' : 2,
            'date' : None,
            'api_key' : None,
        })
        with self.assertRaises(CLIException) as error:
            generate_args(['route', 'info', '99', '--schedule', 'foo'])
        self.check_error_message(error, "argument --schedule: invalid int value: 'foo'")
        args = generate_args(['route', 'info', '99', '--date', '01/01/2019'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'info',
            'route_number' : 99,
            'schedule' : None,
            'date' : '01/01/2019',
            'api_key' : None,
        })
        with self.assertRaises(CLIException) as error:
            generate_args(['route', 'info', '99', '--date', 'derp'])
        self.check_error_message(error, "argument --date: String:derp does "\
                                        "not match regex:%s" % DATE_REGEX)
        args = generate_args(['route', 'info', '99', '--schedule', '2', '--date', '01/01/2019'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'info',
            'route_number' : 99,
            'schedule' : 2,
            'date' : '01/01/2019',
            'api_key' : None,
        })

    def test_station_args(self): # pylint:disable=too-many-statements
        '''
        Test station args
        '''
        # Basic commands
        with self.assertRaises(CLIException) as error:
            generate_args(['station'])
        self.check_error_message(error, "Error: No sub-command arg present")

        with self.assertRaises(CLIException) as error:
            generate_args(['station', ''])
        self.check_error_message(error, "argument subcommand: invalid choice: '' "\
                                        "(choose from 'list', 'info', "\
                                        "'departures', 'access', 'schedule')")
        # Station list
        args = generate_args(['station', 'list'])
        self.assert_dictionary(args, {
            'command' : 'station',
            'subcommand' : 'list',
            'api_key' : None,
        })
        # Station info
        with self.assertRaises(CLIException) as error:
            generate_args(['station', 'info'])
        self.check_error_message(error, "the following arguments are required: station")
        with self.assertRaises(CLIException) as error:
            generate_args(['station', 'info', 'and erg'])
        self.check_error_message(error, "argument station: String:and erg does "\
                                        "not match regex:%s" % STATION_REGEX)
        args = generate_args(['station', 'info', 'dubl'])
        self.assert_dictionary(args, {
            'command' : 'station',
            'subcommand' : 'info',
            'station' : 'dubl',
            'api_key' : None,
        })
        # Station departures
        with self.assertRaises(CLIException) as error:
            generate_args(['station', 'departures'])
        self.check_error_message(error, "the following arguments are required: station")
        with self.assertRaises(CLIException) as error:
            generate_args(['station', 'departures', 'not valid'])
        self.check_error_message(error, "argument station: String:not valid does "\
                                        "not match regex:%s" % STATION_REGEX)
        args = generate_args(['station', 'departures', 'dubl'])
        self.assert_dictionary(args, {
            'command' : 'station',
            'subcommand' : 'departures',
            'station' : 'dubl',
            'direction' : None,
            'platform' : None,
            'destinations' : None,
            'api_key' : None,
        })
        with self.assertRaises(CLIException) as error:
            generate_args(['station', 'departures', 'dubl', '--direction', 'foo'])
        self.check_error_message(error, "argument --direction: String:foo does not "\
                                        "match regex:%s" % DIRECTION_REGEX)

        args = generate_args(['station', 'departures', 'dubl', '--direction', 'n'])
        self.assert_dictionary(args, {
            'command' : 'station',
            'subcommand' : 'departures',
            'station' : 'dubl',
            'direction' : 'n',
            'platform' : None,
            'destinations' : None,
            'api_key' : None,
        })
        with self.assertRaises(CLIException) as error:
            generate_args(['station', 'departures', 'dubl', '--destinations'])
        self.check_error_message(error, "argument --destinations: expected at least one argument")
        with self.assertRaises(CLIException) as error:
            generate_args(['station', 'departures', 'dubl', '--destinations', 'not valid'])
        self.check_error_message(error, "argument --destinations: String:not valid " \
                                        "does not match regex:^[a-zA-Z0-9]+$")
        args = generate_args(['station', 'departures', 'dubl', '--destinations', '12th'])
        self.assert_dictionary(args, {
            'command' : 'station',
            'subcommand' : 'departures',
            'station' : 'dubl',
            'direction' : None,
            'platform' : None,
            'destinations' : ['12th'],
            'api_key' : None,
        })
        # Station access
        with self.assertRaises(CLIException) as error:
            generate_args(['station', 'access', 'not valid'])
        self.check_error_message(error, "argument station: String:not valid "\
                                        "does not match regex:^[a-zA-Z0-9]+$")
        args = generate_args(['station', 'access', 'dubl'])
        self.assert_dictionary(args, {
            'command' : 'station',
            'subcommand' : 'access',
            'station' : 'dubl',
            'api_key' : None,
        })
        # Schedule
        with self.assertRaises(CLIException) as error:
            generate_args(['station', 'schedule', 'not valid'])
        self.check_error_message(error, "argument station: String:not valid "\
                                        "does not match regex:^[a-zA-Z0-9]+$")
        args = generate_args(['station', 'schedule', 'dubl'])
        self.assert_dictionary(args, {
            'command' : 'station',
            'subcommand' : 'schedule',
            'station' : 'dubl',
            'date' : None,
            'api_key' : None,
        })
        with self.assertRaises(CLIException) as error:
            generate_args(['station', 'schedule', 'dubl', '--date', 'foo'])
        self.check_error_message(error, "argument --date: String:foo does not "\
                                        "match regex:^[0-9]{2}/[0-9]{2}/[0-9]{4}$")
        args = generate_args(['station', 'schedule', 'dubl', '--date', '01/01/2019'])
        self.assert_dictionary(args, {
            'command' : 'station',
            'subcommand' : 'schedule',
            'station' : 'dubl',
            'date' : '01/01/2019',
            'api_key' : None,
        })

    def test_schedule(self):
        '''
        Test schedule args
        '''
        with self.assertRaises(CLIException) as error:
            generate_args(['schedule'])
        self.check_error_message(error, "Error: No sub-command arg present")
        # Schedule List
        args = generate_args(['schedule', 'list'])
        self.assert_dictionary(args, {
            'command' : 'schedule',
            'subcommand' : 'list',
            'api_key' : None,
        })
        # Schedule Fare
        with self.assertRaises(CLIException) as error:
            generate_args(['schedule', 'fare'])
        self.check_error_message(error, "the following arguments are required: "\
                                        "origin_station, destination_station")
        with self.assertRaises(CLIException) as error:
            generate_args(['schedule', 'fare', 'dubl'])
        self.check_error_message(error, "the following arguments are required: destination_station")

        with self.assertRaises(CLIException) as error:
            generate_args(['schedule', 'fare', 'dubl', 'not valid'])
        self.check_error_message(error, "argument destination_station: String:not valid "\
                                        "does not match regex:^[a-zA-Z0-9]+$")
        args = generate_args(['schedule', 'fare', 'dubl', 'mont'])
        self.assert_dictionary(args, {
            'command' : 'schedule',
            'subcommand' : 'fare',
            'origin_station' : 'dubl',
            'destination_station': 'mont',
            'schedule' : None,
            'date' : None,
            'api_key' : None,
        })
        with self.assertRaises(CLIException) as error:
            generate_args(['schedule', 'fare', 'dubl', 'mont', '--schedule', 'foo'])
        self.check_error_message(error, "argument --schedule: invalid int value: 'foo'")
        args = generate_args(['schedule', 'fare', 'dubl', 'mont', '--schedule', '2'])
        self.assert_dictionary(args, {
            'command' : 'schedule',
            'subcommand' : 'fare',
            'origin_station' : 'dubl',
            'destination_station': 'mont',
            'schedule' : 2,
            'date' : None,
            'api_key' : None,
        })
        with self.assertRaises(CLIException) as error:
            generate_args(['schedule', 'fare', 'dubl', 'mont', '--date', 'foo'])
        self.check_error_message(error, "argument --date: String:foo does "\
                                        "not match regex:^[0-9]{2}/[0-9]{2}/[0-9]{4}$")
        args = generate_args(['schedule', 'fare', 'dubl', 'mont', '--date', '01/01/2019'])
        self.assert_dictionary(args, {
            'command' : 'schedule',
            'subcommand' : 'fare',
            'origin_station' : 'dubl',
            'destination_station': 'mont',
            'schedule' : None,
            'date' : '01/01/2019',
            'api_key' : None,
        })
