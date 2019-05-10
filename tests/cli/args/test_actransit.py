from transit.cli.actransit import generate_args
from transit.exceptions import CLIException

from tests.utils import TestRunnerHelper

class TestActransitArgs(TestRunnerHelper):
    def test_no_args(self):
        '''
        Test basic command args throw proper errors
        '''
        with self.assertRaises(CLIException) as error:
            generate_args([''])
        self.check_error_message(error, "argument command: invalid choice: " \
                                        "'' (choose from 'route', 'service', 'stop')")
        with self.assertRaises(CLIException) as error:
            generate_args([])
        self.check_error_message(error, "Error: No command arg present")

    def test_global_args(self):
        '''
        Test global args
        '''

        with self.assertRaises(CLIException) as error:
            generate_args(['-k'])
        self.check_error_message(error, "argument -k/--actransit-api-key: expected one argument")

        args = generate_args(['-k', 'foo', 'route', 'list'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'list',
            'actransit_api_key' : 'foo',
        })

        args = generate_args(['--actransit-api-key', 'foo', 'route', 'list'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'list',
            'actransit_api_key' : 'foo',
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
                                        "'' (choose from 'list', 'directions', 'trips', 'stops')")
        # List commands
        args = generate_args(['-k', 'foo', 'route', 'list'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'list',
            'actransit_api_key' : 'foo',
        })

        # Direction commands
        with self.assertRaises(CLIException) as error:
            generate_args(['-k', 'foo', 'route', 'directions'])
        self.check_error_message(error, "the following arguments are required: route_name")

        args = generate_args(['-k', 'foo', 'route', 'directions', '51A'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'directions',
            'route_name' : '51A',
            'actransit_api_key' : 'foo',
        })

        # Trip commands
        with self.assertRaises(CLIException) as error:
            generate_args(['-k', 'foo', 'route', 'trips'])
        self.check_error_message(error, "the following arguments are required: route_name, "\
                                        "direction")

        with self.assertRaises(CLIException) as error:
            generate_args(['-k', 'foo', 'route', 'trips', '51A'])
        self.check_error_message(error, "the following arguments are required: "\
                                        "direction")

        with self.assertRaises(CLIException) as error:
            generate_args(['-k', 'foo', 'route', 'trips', '51A', '--schedule_type', 'bar'])
        self.check_error_message(error, "argument --schedule_type: invalid choice: 'bar' "\
                                        "(choose from 'weekday', 'saturday', 'sunday')")

        args = generate_args(['-k', 'foo', 'route', 'trips', '51A', 'Southbound'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'trips',
            'route_name' : '51A',
            'direction' : 'Southbound',
            'schedule_type' : 'weekday',
            'actransit_api_key' : 'foo',
        })

        args = generate_args(['-k', 'foo', 'route', 'trips', '51A',
                              'Southbound', '--schedule_type', 'saturday'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'trips',
            'route_name' : '51A',
            'direction' : 'Southbound',
            'schedule_type' : 'saturday',
            'actransit_api_key' : 'foo',
        })

        # Stop commands
        with self.assertRaises(CLIException) as error:
            generate_args(['-k', 'foo', 'route', 'stops'])
        self.check_error_message(error, "the following arguments are required: route_name, "\
                                        "trip_id")

        with self.assertRaises(CLIException) as error:
            generate_args(['-k', 'foo', 'route', 'stops', '51A'])
        self.check_error_message(error, "the following arguments are required: "\
                                        "trip_id")
        args = generate_args(['-k', 'foo', 'route', 'stops', '51A', '1234'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'stops',
            'route_name' : '51A',
            'trip_id' : '1234',
            'actransit_api_key' : 'foo',
        })

    def test_stop_args(self):
        '''
        Test stop args
        '''
        # Basic commands
        with self.assertRaises(CLIException) as error:
            generate_args(['stop'])
        self.check_error_message(error, "Error: No sub-command arg present")

        with self.assertRaises(CLIException) as error:
            generate_args(['stop', ''])
        self.check_error_message(error, "argument subcommand: invalid choice: "\
                                        "'' (choose from 'predictions')")

        with self.assertRaises(CLIException) as error:
            generate_args(['-k', 'foo', 'stop', 'predictions'])
        self.check_error_message(error, "the following arguments are required: stop_id")

        args = generate_args(['-k', 'foo', 'stop', 'predictions', '1234'])
        self.assert_dictionary(args, {
            'command' : 'stop',
            'subcommand' : 'predictions',
            'stop_id' : '1234',
            'actransit_api_key' : 'foo',
        })

    def test_service_notices(self):
        '''
        Test service notices
        '''
        # Basic commands
        with self.assertRaises(CLIException) as error:
            generate_args(['service'])
        self.check_error_message(error, "Error: No sub-command arg present")

        with self.assertRaises(CLIException) as error:
            generate_args(['service', ''])
        self.check_error_message(error, "argument subcommand: invalid choice: "\
                                        "'' (choose from 'notices')")
        # List commands
        args = generate_args(['-k', 'foo', 'service', 'notices'])
        self.assert_dictionary(args, {
            'command' : 'service',
            'subcommand' : 'notices',
            'actransit_api_key' : 'foo',
        })
