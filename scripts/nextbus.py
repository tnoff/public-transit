import argparse
from datetime import datetime

from prettytable import PrettyTable

from transit import nextbus as client

def parse_args(): #pylint: disable=too-many-locals, too-many-statements
    p = argparse.ArgumentParser(description='Nextbus CLI')

    sub_parser = p.add_subparsers(help='Command', dest='command')

    # Nextbus args
    agency = sub_parser.add_parser('agency', help='Agency commands')
    asp = agency.add_subparsers(help='Sub-command',
                                dest='subcommand')
    asp.add_parser('list', help='List agencies')

    route = sub_parser.add_parser('route', help='Route commands')
    rsp = route.add_subparsers(help='Sub-command',
                               dest='subcommand')

    rl = rsp.add_parser('list', help='List routes by agency')
    rl.add_argument('agency_tag', help='Agency tag')

    rg = rsp.add_parser('get',\
                    help='Get information about specific route')
    rg.add_argument('agency_tag', help='Agency tag')
    rg.add_argument('route_tag', help='Route tag')

    rm = rsp.add_parser('messages', help='Get route alert messages')
    rm.add_argument('agency_tag', help='Agency tag')
    rm.add_argument('route_tag', nargs='+', help='Route tag(s)')

    stop = sub_parser.add_parser('stop', help='Stop commands')
    ssp = stop.add_subparsers(help='Sub-command',
                              dest='subcommand')

    stop_pred = ssp.add_parser('prediction',
                               help='Predict Stop Wait times')
    stop_pred.add_argument('agency_tag', help='Agency tag')
    stop_pred.add_argument('stop_id', help='Stop ID')
    stop_pred.add_argument('--route-tags', nargs='+', help='Route Tag')

    schedule = sub_parser.add_parser('schedule', help='Schedule')
    schedule.add_argument('agency_tag', help='Agency tag')
    schedule.add_argument('route_tag', help='Route tag')

    vehicle = sub_parser.add_parser('vehicle', help='Vehicle')
    vehicle.add_argument('agency_tag', help='Agency tag')
    vehicle.add_argument('route_tag', help='Route tag')
    vehicle.add_argument('epoch_time', type=int, help='Epoch Time')

    return p.parse_args()

def agency_list(_):
    table = PrettyTable(["Agency Title", "Agency Tag", "Region Title"])
    agencies = sorted(client.agency_list(), key=lambda k: k['title'])
    for agency in agencies:
        table.add_row([agency['title'], agency['tag'], agency['region']])
    print table

def route_list(args):
    table = PrettyTable(["Route Title", "Route Tag"])
    routes = sorted(client.route_list(args.agency_tag),
                    key=lambda k: k['title'])
    for route in routes:
        table.add_row([route['title'], route['route_tag']])
    print table

def route_get(args):
    route = client.route_get(args.agency_tag, args.route_tag)
    table = PrettyTable(["Stop Title", "Stop Tag", "Latitude", "Longitude",
                         "Stop ID"])
    stops = sorted(route['stops'], key=lambda k: k['title'])
    for stop in stops:
        table.add_row([stop['title'], stop['stop_tag'], stop['latitude'], stop['longitude'],
                       stop['stop_id']])
    print 'Stops'
    print table

    table = PrettyTable(["Direction Title", "Direction Tag", "Stop Tags"])
    for direction in route['directions']:
        table.add_row([direction['title'], direction['tag'],
                       ", ".join(i for i in direction['stop_tags'])])
    print 'Directions'
    print table

def stop_prediction(args):
    route_preds = client.stop_prediction(args.agency_tag, args.stop_id,
                                         route_tags=args.route_tags)

    routes = sorted(route_preds, key=lambda k: k['route_title'])
    table = PrettyTable(["Route-Direction", "Predictions (M:S)"])
    for route in routes:
        for direction in route['directions']:
            route_string = '%s-%s' % (route['route_title'], direction['title'])
            preds = []
            for pred in direction['predictions']:
                seconds = int(pred['seconds'])
                minutes = seconds / 60
                seconds = seconds % 60
                hours = minutes / 60
                minutes = minutes % 60
                dater = datetime(2016, 1, 1, hours, minutes, seconds)
                if hours < 1:
                    preds.append(dater.strftime('%M:%S'))
                else:
                    preds.append(dater.strftime('%H:%M:%S'))

            predictions = ' ; '.join(i for i in preds)
            table.add_row([route_string, predictions])
    print table

def schedule_get(args):
    schedules = client.schedule_get(args.agency_tag, args.route_tag)
    for r in schedules:
        print r['title'], '-', r['direction'], '-', r['service_class']
        route_times = dict()
        for block in r['blocks']:
            for ss in block['stop_schedules']:
                route_times.setdefault(ss['title'], [])
                if ss['time']:
                    route_times[ss['title']].append(ss['time'])
        table = PrettyTable(["Stop Title", "Expected Time"])
        for rt in route_times:
            for time in route_times[rt]:
                time_str = time.strftime('%H:%M:%S')

                table.add_row([rt, time_str])
        print table

def vehicle_location(args):
    locations = client.vehicle_location(args.agency_tag,
                                        args.route_tag,
                                        args.epoch_time)
    table = PrettyTable(["Vehicle ID", "Latitude", "Longitude", "Predictable",
                         "Speed KM/HR", "Seconds Since Last Report"])
    for l in locations:
        table.add_row([l['vehicle_id'], l['latitude'], l['longitude'], l['predictable'],
                       l['speedkmhr'], l['seconds_since_last_report']])
    print table

def route_messages(args):
    routes = client.route_messages(args.agency_tag, args.route_tag)
    for route in routes:
        print 'Route:', route['route_tag']
        table = PrettyTable(["Message Text", "Priority", "Send to Buses",
                             "Start", "End"])
        for m in route['messages']:
            table.add_row([''.join(i for i in m['text']), m['priority'],
                           m['send_to_buses'], m['start_boundary'], m['end_boundary']])
        print table

FUNCTION_MATCH = {
    'agency' : {
        'list': agency_list,
    },
    'route' : {
        'list' : route_list,
        'get' : route_get,
        'messages' : route_messages,
    },
    'stop' : {
        'prediction' : stop_prediction,
    },
    'schedule' : {
        None: schedule_get,
    },
    'vehicle' : {
        None : vehicle_location,
    },
}

def main():
    args = parse_args()
    # if no subcommand, make none
    try:
        FUNCTION_MATCH[args.command][args.subcommand]
    except AttributeError:
        args.subcommand = None
    function = FUNCTION_MATCH[args.command][args.subcommand]
    # call local function that matches name
    function(args)
