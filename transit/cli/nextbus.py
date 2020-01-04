import sys

from transit import nextbus
from transit.cli.common import CommonArgparse, CommonCLI, DATETIME_FORMAT_NO_DATE
from transit.cli.common import seconds_to_datetime
from transit.exceptions import CLIException

# Keep this out of the class so it can be inherited by trip planner cli
def generate_prediction_list(stop_data):
    agency_data = {}
    for stop in stop_data:
        agency_data.setdefault(stop['agency_title'], [])
        for direction in stop['directions']:
            preds = ' ; '.join(seconds_to_datetime(pred['seconds'])\
                        for pred in direction['predictions'])
            agency_data[stop['agency_title']].append({
                'route' : stop['route_title'],
                'direction' : direction['title'],
                'predictions' : preds,
                'stop' : stop['stop_title'],
            })
    return agency_data

def generate_args(command_line_args):
    p = CommonArgparse(description='Nextbus cli')
    sub_parser = p.add_subparsers(help='Command', dest='command')

    _add_agency(sub_parser)
    _add_route(sub_parser)
    _add_stop(sub_parser)
    return_args = vars(p.parse_args(command_line_args))
    if return_args['command'] is None:
        raise CLIException("Error: No command arg present")
    if return_args['subcommand'] is None:
        raise CLIException("Error: No sub-command arg present")
    return return_args

def _add_agency(sub_parser):
    agency = sub_parser.add_parser('agency', help='Agency commands')
    asp = agency.add_subparsers(help='Sub-command',
                                dest='subcommand')
    asp.add_parser('list', help='List agencies')

def _add_route(sub_parser):
    route = sub_parser.add_parser('route', help='Route commands')
    rsp = route.add_subparsers(help='Sub-command',
                               dest='subcommand')

    rl = rsp.add_parser('list', help='List routes by agency')
    rl.add_argument('agency_tag', help='Agency tag')

    rg = rsp.add_parser('show',
                        help='Get information about specific route')
    rg.add_argument('agency_tag', help='Agency tag')
    rg.add_argument('route_tag', help='Route tag')

    rm = rsp.add_parser('messages', help='Get route alert messages')
    rm.add_argument('agency_tag', help='Agency tag')
    rm.add_argument('route_tag', nargs='+', help='Route tag(s)')

    rs = rsp.add_parser('schedule', help='Get route schedule')
    rs.add_argument('agency_tag', help='Agency tag')
    rs.add_argument('route_tag', help='Route tag')

    vs = rsp.add_parser('vehicle', help='Get vehcile locations')
    vs.add_argument('agency_tag', help='Agency tag')
    vs.add_argument('route_tag', help='Route tag')
    vs.add_argument('epoch_time', type=int, help='Epoch Time')

def _add_stop(sub_parser):
    stop = sub_parser.add_parser('stop', help='Stop commands')
    ssp = stop.add_subparsers(help='Sub-command',
                              dest='subcommand')

    stop_pred = ssp.add_parser('prediction',
                               help='Predict Stop Wait times')
    stop_pred.add_argument('agency_tag', help='Agency tag')
    stop_pred.add_argument('stop_id', help='Stop ID')
    stop_pred.add_argument('--route-tags', nargs='+', help='Route Tag')

class NextbusCLI(CommonCLI):
    def agency_list(self, **kwargs):
        agency_data = nextbus.agency_list(**kwargs)
        print(self._print_table(agency_data))

    def route_list(self, **kwargs):
        route_data = nextbus.route_list(**kwargs)
        print(self._print_table(route_data))

    def route_show(self, **kwargs):
        route_data = nextbus.route_show(**kwargs)
        # Dont care about paths here
        route_data.pop('paths')
        # Save stops for later
        stops = route_data.pop('stops')
        self._print_json(route_data)
        print(self._print_table(stops))

    def route_messages(self, **kwargs):
        route_data = nextbus.route_messages(**kwargs)
        self._print_json(route_data)

    def route_schedule(self, **kwargs):
        route_data = nextbus.schedule_get(**kwargs)
        for route_dir in route_data:
            print("Direction:", route_dir['direction'],
                  "Service Class:", route_dir['service_class'])
            # Combine all blocks
            all_stops = []
            for block in route_dir['blocks']:
                all_stops += block['stop_schedules']
            print(self._print_table(all_stops, datetime_format=DATETIME_FORMAT_NO_DATE,
                                    key_order=['time', 'stop_tag', 'title']))

    def route_vehicle(self, **kwargs):
        route_data = nextbus.vehicle_location(**kwargs)
        print(self._print_table(route_data, key_order=['vehicle_id', 'latitude', 'longitude']))

    def stop_prediction(self, **kwargs):
        stop_data = nextbus.stop_prediction(**kwargs)
        # Generate agency data
        agency_data = generate_prediction_list(stop_data)
        for agency, pred_data in agency_data.items():
            print("Agency:", agency)
            print(self._print_table(pred_data, key_order=['route', 'direction', 'predictions']))

def main():
    try:
        args = generate_args(sys.argv[1:])
        nextbus_cli = NextbusCLI(**args)
        nextbus_cli.run_command()
    except CLIException as exc:
        print(str(exc))
