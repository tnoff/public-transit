import sys

from transit import bart
from transit.cli.common import CommonArgparse, CommonCLI, regex_checker
from transit.exceptions import CLIException
from transit.modules.bart.settings import DATE_REGEX, DIRECTION_REGEX, STATION_REGEX

# DEFAULTS

DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H-%M-%S'

DATETIME_FORMAT_NO_DATE = '%H:%M:%S'

DATETIME_FORMAT_JUST_DATE = '%Y-%m-%d'


# Keep this out of the class so it can be inherited by trip planner cli
def generate_prediction_list(departure_data):
    list_data = []
    for station in departure_data:
        for direction in station['directions']:
            estimates = " ; ".join(str(e['minutes']) for e in direction['estimates'])
            list_data.append({
                'station' : station['name'],
                'direction' : direction['name'],
                'estimates ( minutes )' : estimates,
            })
    return list_data

# Command Line args

def date_regex_checker(stringy):
    return regex_checker(stringy, DATE_REGEX)

def direction_regex_checker(stringy):
    return regex_checker(stringy, DIRECTION_REGEX)

def station_abbr_checker(stringy):
    return regex_checker(stringy, STATION_REGEX)

def generate_args(command_line_args):
    p = CommonArgparse(description='Bart cli')
    sub_parser = p.add_subparsers(help='Command', dest='command')

    _add_service(sub_parser)
    _add_routes(sub_parser)
    _add_stations(sub_parser)
    _add_schedules(sub_parser)
    return_args = vars(p.parse_args(command_line_args))
    if return_args['command'] is None:
        raise CLIException("Error: No command arg present")
    if return_args['subcommand'] is None:
        raise CLIException("Error: No sub-command arg present")
    return return_args

def _add_service(sub_parser):

    service = sub_parser.add_parser('service', help='Service commands')

    service_parser = service.add_subparsers(dest='subcommand',
                                            help='Subcommand')
    service_parser.add_parser('advisory',
                              help='Current Service Advisory')
    service_parser.add_parser('train-count',
                              help='Current Train Count')
    service_parser.add_parser('elevator-status',
                              help='Current Elevator Status')

def _add_routes(sub_parser):
    routes = sub_parser.add_parser('route', help='Route commands')
    routes_sp = routes.add_subparsers(help='Sub-command',
                                      dest='subcommand')
    # List
    route_list = routes_sp.add_parser('list', help="List routes")
    route_list.add_argument('--schedule', type=int,
                            help='Schedule Number')
    route_list.add_argument('--date', type=date_regex_checker, help='MM/DD/YYYY format')
    # Info
    route_show = routes_sp.add_parser('info',
                                      help='Route Information')
    route_show.add_argument('route_number', type=int, help='Route number')
    route_show.add_argument('--schedule', type=int,
                            help='Schedule Number')
    route_show.add_argument('--date', type=date_regex_checker, help='MM/DD/YYYY format')

def _add_stations(sub_parser):
    stations = sub_parser.add_parser('station', help='Station Commands')
    stations_sp = stations.add_subparsers(help='Sub-command',
                                          dest='subcommand')
    # List
    stations_sp.add_parser('list', help='List stations')
    # Info
    station_infos = stations_sp.add_parser('info',
                                           help='Show station info')
    station_infos.add_argument('station_abbr', type=station_abbr_checker,
                               help='Station Abbreviation')
    # Departures
    est = stations_sp.add_parser('departures',
                                 help='Estimates for a station')
    est.add_argument('station_abbr', type=station_abbr_checker,
                     help='Station Abbreviation or "all"')
    est.add_argument('--direction', type=direction_regex_checker,
                     help='(n)orth or (s)outh')
    est.add_argument('--platform', type=int, help='Platform Number')
    est.add_argument('--destinations', nargs='+', type=station_abbr_checker,
                     help='Only show these desination abbreviatons')
    # Access
    station_access = stations_sp.add_parser('access',
                                            help='Show station access')
    station_access.add_argument('station_abbr',
                                type=station_abbr_checker,
                                help='Station Abbreviation')
    # Schedule
    station_sched = stations_sp.add_parser('schedule',
                                           help='Station Schedule')
    station_sched.add_argument('station_abbr',
                               type=station_abbr_checker,
                               help='Station abbreviation')
    station_sched.add_argument('--date', type=date_regex_checker,
                               help='MM/DD/YYYY format')

def _add_schedules(sub_parser):
    schedule = sub_parser.add_parser('schedule', help='Schedule Commands')
    schedule_sp = schedule.add_subparsers(help='Sub-command',
                                          dest='subcommand')
    # Schedule List
    schedule_sp.add_parser('list', help='Schedule List')
    # Schedule Fare
    schedule_fare = schedule_sp.add_parser('fare',
                                           help='Get fare information')
    schedule_fare.add_argument('origin_station',
                               type=station_abbr_checker,
                               help='Origin Station')
    schedule_fare.add_argument('destination_station',
                               type=station_abbr_checker,
                               help='Destination Station')
    schedule_fare.add_argument('--schedule', type=int,
                               help='Schedule Number')
    schedule_fare.add_argument('--date',
                               type=date_regex_checker,
                               help='MM/DD/YYYY format')
class BartCLI(CommonCLI):
    def service_advisory(self, **kwargs):
        advisories = bart.service_advisory(**kwargs)
        self._print_json(advisories)

    def service_train_count(self, **kwargs):
        count = bart.train_count(**kwargs)
        self._print_json(count)

    def service_elevator_status(self, **kwargs):
        status = bart.elevator_status(**kwargs)
        self._print_json(status)

    def route_list(self, **kwargs):
        list_data = bart.route_list(**kwargs)
        print("Schedule Number:%s" % list_data['schedule_number'])
        self._print_table(list_data['routes'])

    def route_info(self, **kwargs):
        route_data = bart.route_info(**kwargs)
        self._print_json(route_data)

    def station_list(self, **kwargs):
        list_data = []
        station_data = bart.station_list(**kwargs)
        # Ensure go through keys sorted to be consistent
        keys = sorted(list(station_data.keys()))
        for key in keys:
            list_data.append({
                'abbreviation' : key,
                'name' : station_data[key]
            })
        self._print_table(list_data)

    def station_info(self, **kwargs):
        station_data = bart.station_info(**kwargs)
        self._print_json(station_data)

    def station_departures(self, **kwargs):
        departure_data = bart.station_departures(**kwargs)
        list_data = generate_prediction_list(departure_data)
        self._print_table(list_data, key_order=['station', 'direction', 'estimates ( minutes )'])

    def station_access(self, **kwargs):
        station_data = bart.station_access(**kwargs)
        self._print_json(station_data)

    def station_schedule(self, **kwargs):
        station_data = bart.station_schedule(**kwargs)
        print("Station Name:", station_data['name'])
        self._print_table(station_data['schedule_times'],
                          datetime_format=DATETIME_FORMAT_NO_DATE,
                          key_order=['line', 'origin_time', 'destination_time', 'bike_flag'])

    def schedule_list(self, **kwargs):
        schedule_data = bart.schedule_list(**kwargs)
        self._print_table(schedule_data, datetime_format=DATETIME_FORMAT_JUST_DATE,
                          key_order=['id', 'effective_date'])

    def schedule_fare(self, **kwargs):
        schedule_data = bart.schedule_fare(**kwargs)
        self._print_json(schedule_data)


def main():
    try:
        args = generate_args(sys.argv[1:])
        bart_cli = BartCLI(**args)
        bart_cli.run_command()
    except CLIException as exc:
        print(str(exc))
