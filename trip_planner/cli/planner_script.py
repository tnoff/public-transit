import os
import sys

from transit.cli.bart import generate_prediction_list as bart_pred_list
from transit.cli.bart import DEFAULT_BART_API_KEY
from transit.cli.nextbus import generate_prediction_list as nextbus_pred_list
from transit.cli.common import CommonArgparse, CommonCLI
from transit.exceptions import CLIException

from trip_planner.client import TripPlanner

DEFAULT_DB_PATH = os.path.join(os.path.expanduser('~'),
                               '.trip_planner',
                               'planner.sql')

def create_directory(path):
    try:
        os.mkdir(path)
    except OSError as e:
        if 'File exists' in str(e):
            pass
        else:
            raise OSError(e)

def generate_args(command_line_args):
    p = CommonArgparse(description='Planner Script CLI')

    p.add_argument('-d', '--db-file', default=DEFAULT_DB_PATH,
                   help='Path to local db file')
    p.add_argument('-b', '--bart-api-key', default=DEFAULT_BART_API_KEY,
                   help='Use specific bart api key')

    sub_parser = p.add_subparsers(help='Command', dest='command')

    _add_leg(sub_parser)
    _add_trips(sub_parser)

    return_args = vars(p.parse_args(command_line_args))
    if return_args['command'] is None:
        raise CLIException("Error: No command arg present")
    if return_args['subcommand'] is None:
        raise CLIException("Error: No sub-command arg present")
    return return_args

def _add_leg(subparsers):
    leg = subparsers.add_parser('leg', help='Let of a trip')
    leg_parsers = leg.add_subparsers(dest='subcommand',
                                     help='Sub-Command')

    leg_create = leg_parsers.add_parser('create',
                                        help='Create leg')
    leg_create.add_argument('agency_tag',
                            help='actransit, bart, sf-muni, etc..')
    leg_create.add_argument('stop_id',
                            help='ID of stop or station abbreviation')
    leg_create.add_argument('--destinations', nargs='+',
                            help='Include destination or route tag')
    leg_create.add_argument('--force', action='store_true',
                            help='Do not check destinations')

    leg_parsers.add_parser('list', help='List legs')

    leg_delete = leg_parsers.add_parser('delete', help='Delete Leg')
    leg_delete.add_argument('leg_id', type=int, nargs='+', help='Leg ID number')

    leg_show = leg_parsers.add_parser('show', help='Show leg')
    leg_show.add_argument('leg_id', type=int, help='Leg ID number')

def _add_trips(subparsers):
    trips = subparsers.add_parser('trip', help='Trip commands')
    trips_parsers = trips.add_subparsers(dest='subcommand', help='Sub-Command')

    trips_parsers.add_parser('list', help='List trips')

    trips_create = trips_parsers.add_parser('create', help='Create trip')
    trips_create.add_argument('name', help='Trip Name')
    trips_create.add_argument('legs', type=int, nargs='+', help='Leg IDs')

    trips_show = trips_parsers.add_parser('show', help='Show trip')
    trips_show.add_argument('trip_id', type=int, help='Trip ID')

    trips_delete = trips_parsers.add_parser('delete', help='Delete trip')
    trips_delete.add_argument('trip_id', type=int, nargs='+', help='Trip ID')


class TripPlannerCLI(CommonCLI):
    def __init__(self, **kwargs):
        CommonCLI.__init__(self, **kwargs)
        # Reset kwargs so db file doesnt show up
        db_file = kwargs.pop('db_file')
        kwargs.pop('command')
        kwargs.pop('subcommand')
        self.kwargs = kwargs
        db_dir_path = os.path.split(db_file)[0]
        create_directory(db_dir_path)
        self.planner = TripPlanner(database_path=db_file)

    def leg_list(self, **kwargs):
        leg_data = self.planner.leg_list(**kwargs)
        for leg in leg_data:
            leg['destinations'] = ' ; '.join(dest for dest in leg['destinations'])
        self._print_table(leg_data, key_order=['id', 'agency', 'stop_title',
                                               'stop_tag', 'destinations'])

    def leg_create(self, **kwargs):
        leg_data = self.planner.leg_create(**kwargs)
        print("Leg created:", leg_data.pop('id'))
        self._print_json(leg_data)

    def leg_show(self, **kwargs):
        agency, leg_data = self.planner.leg_show(**kwargs)
        if agency == 'bart':
            print("Agency: bart")
            list_data = bart_pred_list(leg_data)
            self._print_table(list_data, key_order=['station', 'direction',
                                                    'estimates ( minutes )'])
        else:
            agency_data = nextbus_pred_list(leg_data)
            for agency, pred_data in agency_data.items():
                print("Agency:", agency)
                self._print_table(pred_data, key_order=['stop', 'route',
                                                        'direction', 'predictions'])

    def leg_delete(self, **kwargs):
        leg_data = self.planner.leg_delete(**kwargs)
        print("Legs deleted:", " ; ".join(str(leg) for leg in leg_data))

    def trip_create(self, **kwargs):
        trip_data = self.planner.trip_create(**kwargs)
        print("Trip created:", trip_data.pop('id'))
        self._print_json(trip_data)

    def trip_list(self, **kwargs):
        trip_data = self.planner.trip_list(**kwargs)
        for trip in trip_data:
            trip['legs'] = ' ; '.join(str(leg) for leg in trip['legs'])
        self._print_table(trip_data, key_order=['id', 'name', 'legs'])

    def trip_delete(self, **kwargs):
        trip_data = self.planner.trip_delete(**kwargs)
        print("Trips deleted:", " ; ".join(str(trip) for trip in trip_data))

    def trip_show(self, **kwargs):
        trip_data = self.planner.trip_show(**kwargs)

        bart_data = trip_data.pop('bart', None)
        if bart_data:
            print("Agency: bart")
            list_data = bart_pred_list(bart_data)
            self._print_table(list_data, key_order=['station', 'direction',
                                                    'estimates ( minutes )'])
        nextbus_data = trip_data.pop('nextbus', None)
        if nextbus_data:
            agency_data = nextbus_pred_list(nextbus_data)
            for agency, pred_data in agency_data.items():
                print("Agency:", agency)
                self._print_table(pred_data, key_order=['stop', 'route',
                                                        'direction', 'predictions'])

def main():
    try:
        args = generate_args(sys.argv[1:])
        trip_planner_cli = TripPlannerCLI(**args)
        trip_planner_cli.run_command()
    except CLIException as exc:
        print(str(exc))
