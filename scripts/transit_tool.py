from transit import client

import argparse
from prettytable import PrettyTable

MATCH = {
    'nextbus' : {
        'agency' : {'list': 'agency_list'},
        'route' : {'list' : 'route_list',
                   'get' : 'route_get'},
        'stop' : {'prediction' : 'stop_prediction',
                  'multi_prediction' : 'multi_prediction',},
        'schedule' : {None: 'schedule_get'},
        'vehicle' : {None : 'vehicle_location'},
        'message' : {None : 'message_get'},
    },
    'bart' : {
        'service' : {'advisory' : 'service_advisory',
                     'train-count': 'train_count',
                      'elevator-status' : 'elevator_status',},
        'route': {'list' : 'bart_current_routes',
                  'info' : 'bart_route_info'},
        'station' : {'list' : 'bart_station_list',
                     'info' : 'bart_station_info',
                     'access' : 'bart_station_access',
                     'departures' : 'estimated_departures'},
        'schedule' : {'list' : 'bart_schedule_list',},
    },
}

def parse_args(): #pylint: disable=too-many-locals
    p = argparse.ArgumentParser(description='Public Transit CLI')

    module_sub_parser = p.add_subparsers(help='Module', dest='module')

    # Nextbus args
    nextbus = module_sub_parser.add_parser('nextbus', help='Nextbus Module')
    nextbus_parser = nextbus.add_subparsers(help='Command', dest='command')

    nextbus_agency = nextbus_parser.add_parser('agency', help='Agency commands')
    nextbus_asp = nextbus_agency.add_subparsers(help='Sub-command',
                                                dest='subcommand')
    nextbus_asp.add_parser('list', help='List agencies')

    nextbus_route = nextbus_parser.add_parser('route', help='Route commands')
    nextbus_rsp = nextbus_route.add_subparsers(help='Sub-command',
                                               dest='subcommand')

    nextbus_rl = nextbus_rsp.add_parser('list', help='List routes by agency')
    nextbus_rl.add_argument('agency_tag', help='Agency tag')

    nextbus_rg = nextbus_rsp.add_parser('get',
                                        help='Get information about specific route')
    nextbus_rg.add_argument('agency_tag', help='Agency tag')
    nextbus_rg.add_argument('route_tag', help='Route tag')

    nextbus_stop = nextbus_parser.add_parser('stop', help='Stop commands')
    nextbus_ssp = nextbus_stop.add_subparsers(help='Sub-command',
                                              dest='subcommand')

    nextbus_stop_pred = nextbus_ssp.add_parser('prediction',
                                               help='Predict Stop Wait times')
    nextbus_stop_pred.add_argument('agency_tag', help='Agency tag')
    nextbus_stop_pred.add_argument('stop_id', help='Stop ID')
    nextbus_stop_pred.add_argument('--route-tag', help='Route Tag')

    nextbus_schedule = nextbus_parser.add_parser('schedule', help='Schedule')
    nextbus_schedule.add_argument('agency_tag', help='Agency tag')
    nextbus_schedule.add_argument('route_tag', help='Route tag')

    nextbus_vehicle = nextbus_parser.add_parser('vehicle', help='Vehicle')
    nextbus_vehicle.add_argument('agency_tag', help='Agency tag')
    nextbus_vehicle.add_argument('route_tag', help='Route tag')
    nextbus_vehicle.add_argument('epoch_time', type=int, help='Epoch Time')

    nextbus_message = nextbus_parser.add_parser('message', help='Messages')
    nextbus_message.add_argument('agency_tag', help='Agency tag')
    nextbus_message.add_argument('route_tag', nargs='+', help='Route tag(s)')

    # Bart args
    bart = module_sub_parser.add_parser('bart', help='Bart Module')
    bart_parser = bart.add_subparsers(help='Command', dest='command')

    bart_service = bart_parser.add_parser('service', help='Service commands')
    bart_service_parser = bart_service.add_subparsers(dest='subcommand',
                                                      help='Subcommand')

    bart_service_parser.add_parser('advisory',
                                   help='Current Service Advisory')

    bart_service_parser.add_parser('train-count',
                                   help='Current Train Count')

    bart_service_parser.add_parser('elevator-status',
                                   help='Current Elevator Status')

    bart_routes = bart_parser.add_parser('route', help='Route commands')
    bart_routes_sp = bart_routes.add_subparsers(help='Sub-command',
                                                dest='subcommand')
    bart_route_list = bart_routes_sp.add_parser('list', help="List routes")
    bart_route_list.add_argument('--schedule', type=int,
                                 help='Schedule Number')
    bart_route_list.add_argument('--date', help='MM/DD/YYYY format')

    bart_route_show = bart_routes_sp.add_parser('info',
                                                help='Route Information')
    bart_route_show.add_argument('route_number', help='Route number')
    bart_route_show.add_argument('--schedule', type=int,
                                 help='Schedule Number')
    bart_route_show.add_argument('--date', help='MM/DD/YYYY format')

    bart_stations = bart_parser.add_parser('station', help='Station Commands')
    bart_stations_sp = bart_stations.add_subparsers(help='Sub-command',
                                                    dest='subcommand')
    bart_stations_sp.add_parser('list', help='List stations')

    bart_station_infos = bart_stations_sp.add_parser('info',
                                                     help='Show station info')
    bart_station_infos.add_argument('station',
                                   help='Station Abbreviation')
    bart_est = bart_stations_sp.add_parser('departures',
                                           help='Estimates for a station')
    bart_est.add_argument('station', help='Station Abbreviation or "all"')
    bart_est.add_argument('--direction', help='(n)orth or (s)outh')
    bart_est.add_argument('--platform', type=int, help='Platform Number')


    bart_station_accessy = bart_stations_sp.add_parser('access',
                                                       help='Show station access')
    bart_station_accessy.add_argument('station',
                                     help='Station Abbreviation')

    bart_schedule = bart_parser.add_parser('schedule', help='Schedule Commands')
    bart_schedule_sp = bart_schedule.add_subparsers(help='Sub-command',
                                                    dest='subcommand')

    bart_schedule_sp.add_parser('list', help='Schedule List')

    return p.parse_args()

def agency_list(_):
    table = PrettyTable(["Agency Title", "Agency Tag", "Region Title"])
    agencies = sorted(client.nextbus.agency_list(), key=lambda k: k.title)
    for agency in agencies:
        table.add_row([agency.title, agency.tag, agency.region])
    print table

def route_list(args):
    table = PrettyTable(["Route Title", "Route Tag"])
    routes = sorted(client.nextbus.route_list(args.agency_tag), key=lambda k: k.title)
    for route in routes:
        table.add_row([route.title, route.route_tag])
    print table

def route_get(args):
    route = client.nextbus.route_get(args.agency_tag, args.route_tag)
    table = PrettyTable(["Stop Title", "Stop Tag", "Latitude", "Longitude",
                         "Stop ID"])
    stops = sorted(route.stops, key=lambda k: k.title)
    for stop in stops:
        table.add_row([stop.title, stop.tag, stop.latitude, stop.longitude,
                       stop.stop_id])
    print 'Stops'
    print table

    table = PrettyTable(["Direction Title", "Direction Tag", "Stop Tags"])
    for direction in route.directions:
        table.add_row([direction.title, direction.tag,
                      ", ".join(i for i in direction.stop_tags)])
    print 'Directions'
    print table

def stop_prediction(args):
    route_preds = client.nextbus.stop_prediction(args.agency_tag, args.stop_id,
                                  route_tag=args.route_tag)

    routes = sorted(route_preds, key=lambda k: k.route_title)
    table = PrettyTable(["Route-Direction", "Predictions (M-S)"])
    for route in routes:
        for direction in route.directions:
            route_string = '%s-%s' % (route.route_title, direction.title)
            preds = ['%s-%s' % (i.minutes, (i.seconds - (i.minutes * 60))) \
                        for i in direction.predictions]
            predictions = ', '.join(i for i in preds)
            table.add_row([route_string, predictions])
    print table

def schedule_get(args):
    schedules = client.nextbus.schedule_get(args.agency_tag, args.route_tag)
    for r in schedules:
        print r.title, '-', r.direction, '-', r.service_class
        route_times = dict()
        for b in r.blocks:
            for ss in b.stop_schedules:
                route_times.setdefault(ss.title, [])
                if ss.time:
                    route_times[ss.title].append(ss.time)
        table = PrettyTable(["Stop Title", "Expected Time"])
        for rt in route_times:
            for time in route_times[rt]:
                table.add_row([rt, '%s-%s-%s' % \
                    (time.hour, time.minute, time.second)])
        print table

def vehicle_location(args):
    locations = client.nextbus.vehicle_location(args.agency_tag,
                                        args.route_tag,
                                        args.epoch_time)
    table = PrettyTable(["Vehicle ID", "Latitude", "Longitude", "Predictable",
                         "Speed KM/HR", "Seconds Since Last Report"])
    for l in locations:
        table.add_row([l.vehicle_id, l.latitude, l.longitude, l.predictable,
                       l.speed_km_hr, l.seconds_since_last_report])
    print table

def message_get(args):
    routes = client.nextbus.message_get(args.agency_tag, args.route_tag)
    for route in routes:
        print 'Route:', route.title
        table = PrettyTable(["Message Text", "Priority", "Send to Buses",
                             "Start", "End"])
        for m in route.messages:
            table.add_row([''.join(i for i in m.text), m.priority,
                           m.send_to_buses, m.start_boundary, m.end_boundary])
        print table

def service_advisory(_):
    advisories = client.bart.service_advisory()
    table = PrettyTable(["Station", "Posted", "Description"])
    for advisory in advisories:
        table.add_row([advisory.station, advisory.posted, advisory.description])
    print table

def train_count(_):
    print client.bart.train_count()

def elevator_status(_):
    status = client.bart.elevator_status()
    print status.description

def estimated_departures(args):
    estimates = client.bart.estimated_departures(args.station,
                                                 platform=args.platform,
                                                 direction=args.direction)
    table = PrettyTable(["Station", "Direction", "Estimates"])
    for estimate in estimates:
        for direction in estimate.directions:
            data = [estimate.name]
            data.append(direction.name)
            data.append(';'.join('%s' % i for i in direction.estimates))
            table.add_row(data)
    print table

def bart_current_routes(args):
    schedule = client.bart.current_routes(schedule=args.schedule,
                                         date=args.date)
    print 'Schedule Number:', schedule.schedule_number
    table = PrettyTable(["Name", "Number", "Color"])
    for route in schedule.routes:
        table.add_row([route.name, route.number, route.color])
    print table

def bart_route_info(args):
    route = client.bart.route_info(args.route_number,
                                   schedule=args.schedule,
                                   date=args.date)
    table = PrettyTable(["Name", "Number", "Color"])
    table.add_row([route.name, route.number, route.color])
    print table

def bart_station_list(_):
    stations = client.bart.station_list()
    ordered_stations = [(k, stations[k]) for k in stations]
    ordered_stations.sort(key=lambda x: x[0])
    table = PrettyTable(["Abbreviation", "Name"])
    for item in ordered_stations:
        table.add_row([item[0], item[1]])
    print table

def bart_station_info(args):
    station = client.bart.station_info(args.station)
    print 'Station:', station.name
    print 'Address:', station.address, station.city, station.state
    print 'North Routes:', ';'.join('%s' % i for i in station.north_routes)
    print 'South Routes:', ';'.join('%s' % i for i in station.south_routes)

def bart_station_access(args):
    station = client.bart.station_access(args.station)
    print 'Station:', station.name
    print 'Entering:', station.entering
    print 'Exiting:', station.exiting

def bart_schedule_list(_):
    schedules = client.bart.schedule_list()
    table = PrettyTable(["ID", "Effective Date"])
    for sched in schedules:
        table.add_row([sched.id, sched.effective_date])
    print table

def main():
    args = parse_args()
    # if no subcommand, make none
    try:
        MATCH[args.module][args.command][args.subcommand]
    except AttributeError:
        args.subcommand = None
    function = MATCH[args.module][args.command][args.subcommand]
    # call local function that matches name
    globals()[function](args)
