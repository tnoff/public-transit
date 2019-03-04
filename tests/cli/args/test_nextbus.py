from transit.cli.nextbus import generate_args
from transit.exceptions import CLIException

from tests.utils import TestRunnerHelper

class TestNextbusArgs(TestRunnerHelper):
    def test_no_args(self):
        '''
        Test basic command args throw proper errors
        '''
        with self.assertRaises(CLIException) as error:
            generate_args([''])
        self.check_error_message(error, "argument command: invalid choice: "\
                                        "'' (choose from 'agency', 'route', "\
                                        "'stop')")
        with self.assertRaises(CLIException) as error:
            generate_args([])
        self.check_error_message(error, "Error: No command arg present")

    def test_agency_args(self):
        '''
        Test agency commands
        '''
        # Basic commands
        with self.assertRaises(CLIException) as error:
            generate_args(['agency'])
        self.check_error_message(error, "Error: No sub-command arg present")

        with self.assertRaises(CLIException) as error:
            generate_args(['agency', ''])
        self.check_error_message(error, "argument subcommand: invalid choice: "\
                                        "'' (choose from 'list')")
        # Each subcommand
        args = generate_args(['agency', 'list'])
        self.assert_dictionary(args, {
            'command' : 'agency',
            'subcommand' : 'list'
        })

    def test_route_args(self):
        '''
        Test route commands
        '''
        # Basic commands
        with self.assertRaises(CLIException) as error:
            generate_args(['route'])
        self.check_error_message(error, "Error: No sub-command arg present")

        with self.assertRaises(CLIException) as error:
            generate_args(['route', ''])
        self.check_error_message(error, "argument subcommand: invalid choice: "\
                                        "'' (choose from 'list', 'show', 'messages', "\
                                        "'schedule', 'vehicle')")
        # Each subcommand

        # Route list
        with self.assertRaises(CLIException) as error:
            generate_args(['route', 'list'])
        self.check_error_message(error, "the following arguments are required: agency_tag")

        args = generate_args(['route', 'list', 'sf-muni'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'list',
            'agency_tag' : 'sf-muni',
        })

        # Route show
        with self.assertRaises(CLIException) as error:
            generate_args(['route', 'show'])
        self.check_error_message(error, "the following arguments are required: "\
                                        "agency_tag, route_tag")
        with self.assertRaises(CLIException) as error:
            generate_args(['route', 'show', 'sf-muni'])
        self.check_error_message(error, "the following arguments are required: "\
                                        "route_tag")

        args = generate_args(['route', 'show', 'sf-muni', 'J'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'show',
            'agency_tag' : 'sf-muni',
            'route_tag' : 'J',
        })

        # Route messages
        with self.assertRaises(CLIException) as error:
            generate_args(['route', 'messages'])
        self.check_error_message(error, "the following arguments are required: "\
                                        "agency_tag, route_tag")
        with self.assertRaises(CLIException) as error:
            generate_args(['route', 'messages', 'sf-muni'])
        self.check_error_message(error, "the following arguments are required: "\
                                        "route_tag")

        args = generate_args(['route', 'messages', 'sf-muni', 'J'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'messages',
            'agency_tag' : 'sf-muni',
            'route_tag' : ['J'],
        })

        # Route schedule
        with self.assertRaises(CLIException) as error:
            generate_args(['route', 'schedule'])
        self.check_error_message(error, "the following arguments are required: "\
                                        "agency_tag, route_tag")
        with self.assertRaises(CLIException) as error:
            generate_args(['route', 'schedule', 'sf-muni'])
        self.check_error_message(error, "the following arguments are required: "\
                                        "route_tag")

        args = generate_args(['route', 'schedule', 'sf-muni', 'J'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'schedule',
            'agency_tag' : 'sf-muni',
            'route_tag' : 'J',
        })

        # Route vehicle
        with self.assertRaises(CLIException) as error:
            generate_args(['route', 'vehicle'])
        self.check_error_message(error, "the following arguments are required: "\
                                        "agency_tag, route_tag, epoch_time")
        with self.assertRaises(CLIException) as error:
            generate_args(['route', 'vehicle', 'sf-muni'])
        self.check_error_message(error, "the following arguments are required: "\
                                        "route_tag, epoch_time")
        with self.assertRaises(CLIException) as error:
            generate_args(['route', 'vehicle', 'sf-muni', "J"])
        self.check_error_message(error, "the following arguments are required: "\
                                        "epoch_time")
        with self.assertRaises(CLIException) as error:
            generate_args(['route', 'vehicle', 'sf-muni', 'J', 'foo'])
        self.check_error_message(error, "argument epoch_time: invalid int value: 'foo'")

        args = generate_args(['route', 'vehicle', 'sf-muni', 'J', '1235'])
        self.assert_dictionary(args, {
            'command' : 'route',
            'subcommand' : 'vehicle',
            'agency_tag' : 'sf-muni',
            'route_tag' : 'J',
            'epoch_time' : 1235,
        })

    def test_stop_args(self):
        '''
        Test stop commands
        '''
        # Basic commands
        with self.assertRaises(CLIException) as error:
            generate_args(['stop'])
        self.check_error_message(error, "Error: No sub-command arg present")

        with self.assertRaises(CLIException) as error:
            generate_args(['stop', ''])
        self.check_error_message(error, "argument subcommand: invalid choice: '' "\
                                        "(choose from 'prediction')")
        # Each subcommand

        # Stop predictions
        with self.assertRaises(CLIException) as error:
            generate_args(['stop', 'prediction'])
        self.check_error_message(error, "the following arguments are required: agency_tag, stop_id")

        with self.assertRaises(CLIException) as error:
            generate_args(['stop', 'prediction', 'sf-muni'])
        self.check_error_message(error, "the following arguments are required: stop_id")

        args = generate_args(['stop', 'prediction', 'sf-muni', '12345'])
        self.assert_dictionary(args, {
            'command' : 'stop',
            'subcommand' : 'prediction',
            'agency_tag' : 'sf-muni',
            'stop_id' : '12345',
            'route_tags' : None,
        })

        args = generate_args(['stop', 'prediction', 'sf-muni', '12345', '--route-tags', '52', 'J'])
        self.assert_dictionary(args, {
            'command' : 'stop',
            'subcommand' : 'prediction',
            'agency_tag' : 'sf-muni',
            'stop_id' : '12345',
            'route_tags' : ['52', 'J'],
        })
