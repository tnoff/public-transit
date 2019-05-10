import sys

from transit import actransit

from transit.cli.common import CommonArgparse, CommonCLI
from transit.exceptions import CLIException

def generate_args(command_line_args):
    p = CommonArgparse(description='Actransit cli')

    p.add_argument('-k', '--actransit-api-key',
                   help='Use specific API Key for requests')

    sub_parser = p.add_subparsers(help='Command', dest='command')

    _add_routes(sub_parser)
    _add_service(sub_parser)
    _add_stops(sub_parser)

    return_args = vars(p.parse_args(command_line_args))
    if return_args['command'] is None:
        raise CLIException("Error: No command arg present")
    if return_args['subcommand'] is None:
        raise CLIException("Error: No sub-command arg present")
    return return_args

def _add_routes(sub_parser):
    routes = sub_parser.add_parser('route', help='Route commands')
    routes_sp = routes.add_subparsers(help='Sub-command',
                                      dest='subcommand')
    # List
    routes_sp.add_parser('list', help="List routes")

    # Directions
    route_directions = routes_sp.add_parser('directions',
                                            help="List route directions")
    route_directions.add_argument("route_name", help="Route Name")

    # Trips
    route_trips = routes_sp.add_parser('trips',
                                       help="List route trips")
    route_trips.add_argument("route_name", help="Route Name")
    route_trips.add_argument("direction", help="Direction")
    route_trips.add_argument("--schedule_type",
                             choices=['weekday', 'saturday', 'sunday'],
                             default='weekday',
                             help="Schedule Type")
    # Stops
    route_trips = routes_sp.add_parser('stops',
                                       help="List route stops")
    route_trips.add_argument("route_name", help="Route Name")
    route_trips.add_argument("trip_id", help="Trip Id")

def _add_stops(sub_parser):
    stops = sub_parser.add_parser('stop', help='Stop commands')
    stops_sp = stops.add_subparsers(help='Sub-command',
                                    dest='subcommand')
    # Predictions
    stop_preds = stops_sp.add_parser('predictions', help='Stop predictions')
    stop_preds.add_argument("stop_id", help="Stop Id")

def _add_service(sub_parser):
    service = sub_parser.add_parser('service', help='Service commands')
    service_sp = service.add_subparsers(help='Sub-command',
                                        dest='subcommand')
    # Notices
    service_sp.add_parser('notices', help="Service notices")

class ACTransitCLI(CommonCLI):
    def route_list(self, **kwargs):
        routes = actransit.route_list(**kwargs)
        self._print_table(routes, key_order=['Name', 'RouteId', 'Description'])

    def route_directions(self, **kwargs):
        route_dirs = actransit.route_directions(**kwargs)
        self._print_json(route_dirs)

    def route_trips(self, **kwargs):
        route_trip_data = actransit.route_trips(**kwargs)
        self._print_table(route_trip_data, key_order=['TripId', 'StartTime'])

    def route_stops(self, **kwargs):
        route_stop_data = actransit.route_stops(**kwargs)
        self._print_table(route_stop_data, key_order=['StopId', 'Name',
                                                      'Latitude', 'Longitude', 'ScheduledTime'])

    def stop_predictions(self, **kwargs):
        stop_pred_data = actransit.stop_predictions(**kwargs)
        self._print_table(stop_pred_data, key_order=['RouteName',
                                                     'PredictedDeparture', 'VehicleId'])

    def service_notices(self, **kwargs):
        notices = actransit.service_notices(**kwargs)
        self._print_json(notices)

def main():
    try:
        args = generate_args(sys.argv[1:])
        bart_cli = ACTransitCLI(**args)
        bart_cli.run_command()
    except CLIException as exc:
        print(str(exc))
