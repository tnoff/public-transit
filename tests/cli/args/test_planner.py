from trip_planner.cli.planner_script import generate_args, DEFAULT_DB_PATH
from transit.exceptions import CLIException

from tests.utils import TestRunnerHelper

class TestPlannerArgs(TestRunnerHelper):
    def test_no_args(self):
        '''
        Test basic command args throw proper errors
        '''
        with self.assertRaises(CLIException) as error:
            generate_args([''])
        self.check_error_message(error, "argument command: invalid choice: "\
                                        "'' (choose from 'leg', 'trip')")
        with self.assertRaises(CLIException) as error:
            generate_args([])
        self.check_error_message(error, "Error: No command arg present")


    def test_global_args(self):
        '''
        Test global args
        '''
        args = generate_args(['leg', 'list'])
        self.assert_dictionary(args, {
            'command' : 'leg',
            'subcommand' : 'list',
            'db_file' : DEFAULT_DB_PATH,
        })

        args = generate_args(['-d', 'foo.sql', 'leg', 'list'])
        self.assert_dictionary(args, {
            'command' : 'leg',
            'subcommand' : 'list',
            'db_file' : 'foo.sql',
        })

    def test_leg_args(self):
        '''
        Test leg commands
        '''
        # Basic commands
        with self.assertRaises(CLIException) as error:
            generate_args(['leg'])
        self.check_error_message(error, "Error: No sub-command arg present")

        with self.assertRaises(CLIException) as error:
            generate_args(['leg', ''])
        self.check_error_message(error, "argument subcommand: invalid choice: '' "\
                                        "(choose from 'create', 'list', 'delete', 'show')")

        # Test leg list
        args = generate_args(['leg', 'list'])
        self.assert_dictionary(args, {
            'command' : 'leg',
            'subcommand' : 'list',
            'db_file' : DEFAULT_DB_PATH,
        })

        # Test leg create

        with self.assertRaises(CLIException) as error:
            generate_args(['leg', 'create'])
        self.check_error_message(error, "the following arguments are required: agency_tag, stop_id")

        with self.assertRaises(CLIException) as error:
            generate_args(['leg', 'create', 'sf-muni'])
        self.check_error_message(error, "the following arguments are required: stop_id")

        args = generate_args(['leg', 'create', 'sf-muni', '1235'])
        self.assert_dictionary(args, {
            'command' : 'leg',
            'subcommand' : 'create',
            'agency_tag' : 'sf-muni',
            'stop_id' : '1235',
            'force' : False,
            'destinations' : None,
            'db_file' : DEFAULT_DB_PATH,
            'bart_api_key' : None,
        })

        args = generate_args(['leg', 'create', 'sf-muni', '1235', '--destinations', 'foo', 'bar'])
        self.assert_dictionary(args, {
            'command' : 'leg',
            'subcommand' : 'create',
            'agency_tag' : 'sf-muni',
            'stop_id' : '1235',
            'force' : False,
            'destinations' : ['foo', 'bar'],
            'db_file' : DEFAULT_DB_PATH,
            'bart_api_key' : None,
        })

        args = generate_args(['leg', 'create', 'sf-muni', '1235', '--force'])
        self.assert_dictionary(args, {
            'command' : 'leg',
            'subcommand' : 'create',
            'agency_tag' : 'sf-muni',
            'stop_id' : '1235',
            'force' : True,
            'destinations' : None,
            'db_file' : DEFAULT_DB_PATH,
            'bart_api_key' : None,
        })

        args = generate_args(['leg', 'create', 'sf-muni', '1235', '--bart-api-key', 'foo'])
        self.assert_dictionary(args, {
            'command' : 'leg',
            'subcommand' : 'create',
            'agency_tag' : 'sf-muni',
            'stop_id' : '1235',
            'force' : False,
            'destinations' : None,
            'db_file' : DEFAULT_DB_PATH,
            'bart_api_key' : 'foo',
        })

        # Leg delete
        with self.assertRaises(CLIException) as error:
            generate_args(['leg', 'delete'])
        self.check_error_message(error, "the following arguments are required: leg_id")

        with self.assertRaises(CLIException) as error:
            generate_args(['leg', 'delete', 'foo'])
        self.check_error_message(error, "argument leg_id: invalid int value: 'foo'")

        args = generate_args(['leg', 'delete', '5', '6'])
        self.assert_dictionary(args, {
            'command' : 'leg',
            'subcommand' : 'delete',
            'leg_id' : [5, 6],
            'db_file' : DEFAULT_DB_PATH,
        })

        # Leg show
        with self.assertRaises(CLIException) as error:
            generate_args(['leg', 'show'])
        self.check_error_message(error, "the following arguments are required: leg_id")

        with self.assertRaises(CLIException) as error:
            generate_args(['leg', 'show', 'foo'])
        self.check_error_message(error, "argument leg_id: invalid int value: 'foo'")

        args = generate_args(['leg', 'show', '5'])
        self.assert_dictionary(args, {
            'command' : 'leg',
            'subcommand' : 'show',
            'leg_id' : 5,
            'db_file' : DEFAULT_DB_PATH,
            'bart_api_key' : None,
        })

        args = generate_args(['leg', 'show', '5', '--bart-api-key', 'foo'])
        self.assert_dictionary(args, {
            'command' : 'leg',
            'subcommand' : 'show',
            'leg_id' : 5,
            'db_file' : DEFAULT_DB_PATH,
            'bart_api_key' : 'foo',
        })

    def test_trip_args(self):
        '''
        Test trip commands
        '''
        # Basic commands
        with self.assertRaises(CLIException) as error:
            generate_args(['trip'])
        self.check_error_message(error, "Error: No sub-command arg present")

        with self.assertRaises(CLIException) as error:
            generate_args(['trip', ''])
        self.check_error_message(error, "argument subcommand: invalid choice: '' "\
                                        "(choose from 'list', 'create', 'show', 'delete')")

        # Trip list
        args = generate_args(['trip', 'list'])
        self.assert_dictionary(args, {
            'command' : 'trip',
            'subcommand' : 'list',
            'db_file' : DEFAULT_DB_PATH,
        })

        # Trip show
        with self.assertRaises(CLIException) as error:
            generate_args(['trip', 'show'])
        self.check_error_message(error, "the following arguments are required: trip_id")

        with self.assertRaises(CLIException) as error:
            generate_args(['trip', 'show', 'foo'])
        self.check_error_message(error, "argument trip_id: invalid int value: 'foo'")

        args = generate_args(['trip', 'show', '5'])
        self.assert_dictionary(args, {
            'command' : 'trip',
            'subcommand' : 'show',
            'trip_id' : 5,
            'db_file' : DEFAULT_DB_PATH,
            'bart_api_key' : None,
        })

        args = generate_args(['trip', 'show', '5', '--bart-api-key', 'foo'])
        self.assert_dictionary(args, {
            'command' : 'trip',
            'subcommand' : 'show',
            'trip_id' : 5,
            'db_file' : DEFAULT_DB_PATH,
            'bart_api_key' : 'foo',
        })

        # Trip delete
        with self.assertRaises(CLIException) as error:
            generate_args(['trip', 'delete'])
        self.check_error_message(error, "the following arguments are required: trip_id")

        with self.assertRaises(CLIException) as error:
            generate_args(['trip', 'delete', 'foo'])
        self.check_error_message(error, "argument trip_id: invalid int value: 'foo'")

        args = generate_args(['trip', 'delete', '5', '6'])
        self.assert_dictionary(args, {
            'command' : 'trip',
            'subcommand' : 'delete',
            'trip_id' : [5, 6],
            'db_file' : DEFAULT_DB_PATH,
        })

        # Trip create
        with self.assertRaises(CLIException) as error:
            generate_args(['trip', 'create'])
        self.check_error_message(error, "the following arguments are required: name, legs")

        with self.assertRaises(CLIException) as error:
            generate_args(['trip', 'create', 'foo'])
        self.check_error_message(error, "the following arguments are required: legs")

        with self.assertRaises(CLIException) as error:
            generate_args(['trip', 'create', 'foo', 'bar'])
        self.check_error_message(error, "argument legs: invalid int value: 'bar'")

        args = generate_args(['trip', 'create', 'foo', '5', '6'])
        self.assert_dictionary(args, {
            'command' : 'trip',
            'subcommand' : 'create',
            'name' : 'foo',
            'legs' : [5, 6],
            'db_file' : DEFAULT_DB_PATH,
        })
