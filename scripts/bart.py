'''CLI for Bart Client'''
from transit.modules.bart import client

import argparse
from prettytable import PrettyTable

MATCH = {
    'service' : {'advisory' : 'service_advisory',
                 'train-count': 'train_count',
                 'elevator-status' : 'elevator_status',},
    'route': {'list' : 'current_routes',
              'info' : 'route_info'},
    'station' : {'list' : 'station_list',
                 'info' : 'station_info',
                 'access' : 'station_access',
                 'departures' : 'estimated_departures',
                 'schedule' : 'station_schedule',},
    'schedule' : {'list' : 'schedule_list',
                  'fare' : 'schedule_fare'},
}

def parse_args(): #pylint: disable=too-many-locals, too-many-statements
    p = argparse.ArgumentParser(description='Bart cli')

    sub_parser = p.add_subparsers(help='Command', dest='command')

    service = sub_parser.add_parser('service', help='Service commands')
    service_parser = service.add_subparsers(dest='subcommand',
                                            help='Subcommand')

    service_parser.add_parser('advisory',
                              help='Current Service Advisory')

    service_parser.add_parser('train-count',
                              help='Current Train Count')

    service_parser.add_parser('elevator-status',
                              help='Current Elevator Status')

    routes = sub_parser.add_parser('route', help='Route commands')
    routes_sp = routes.add_subparsers(help='Sub-command',
                                      dest='subcommand')
    route_list = routes_sp.add_parser('list', help="List routes")
    route_list.add_argument('--schedule', type=int,
                            help='Schedule Number')
    route_list.add_argument('--date', help='MM/DD/YYYY format')

    route_show = routes_sp.add_parser('info',
                                      help='Route Information')
    route_show.add_argument('route_number', help='Route number')
    route_show.add_argument('--schedule', type=int,
                            help='Schedule Number')
    route_show.add_argument('--date', help='MM/DD/YYYY format')

    stations = sub_parser.add_parser('station', help='Station Commands')
    stations_sp = stations.add_subparsers(help='Sub-command',
                                          dest='subcommand')
    stations_sp.add_parser('list', help='List stations')

    station_infos = stations_sp.add_parser('info',
                                           help='Show station info')
    station_infos.add_argument('station',
                               help='Station Abbreviation')
    est = stations_sp.add_parser('departures',
                                 help='Estimates for a station')
    est.add_argument('station', help='Station Abbreviation or "all"')
    est.add_argument('--direction', help='(n)orth or (s)outh')
    est.add_argument('--platform', type=int, help='Platform Number')
    est.add_argument('--destinations', nargs='+',
                     help='Only show these desination abbreviatons')

    station_accessy = stations_sp.add_parser('access',\
                            help='Show station access')
    station_accessy.add_argument('station',
                                 help='Station Abbreviation')

    station_sched = stations_sp.add_parser('schedule',
                                           help='Station Schedule')
    station_sched.add_argument('station', help='Station abbreviation')
    station_sched.add_argument('--date', help='MM/DD/YYYY format')

    schedule = sub_parser.add_parser('schedule', help='Schedule Commands')
    schedule_sp = schedule.add_subparsers(help='Sub-command',
                                          dest='subcommand')

    schedule_sp.add_parser('list', help='Schedule List')

    schedule_farey = schedule_sp.add_parser('fare',\
                            help='Get fare information')
    schedule_farey.add_argument('origin_station',
                                help='Origin Station')
    schedule_farey.add_argument('destination_station',
                                help='Destination Station')
    schedule_farey.add_argument('--schedule', type=int,
                                help='Schedule Number')
    schedule_farey.add_argument('--date', help='MM/DD/YYYY format')
    return p.parse_args()

def service_advisory(_):
    advisories = client.service_advisory()
    table = PrettyTable(["Station", "Posted", "Description"])
    for advisory in advisories:
        table.add_row([advisory.station, advisory.posted, advisory.description])
    print table

def train_count(_):
    print client.train_count()

def elevator_status(_):
    status = client.elevator_status()
    print status.description

def estimated_departures(args):
    estimates = client.station_departures(args.station,
                                          platform=args.platform,
                                          direction=args.direction,
                                          destinations=args.destinations)
    table = PrettyTable(["Station", "Direction", "Estimates"])
    for estimate in estimates:
        for direction in estimate.directions:
            data = [estimate.name]
            data.append(direction.name)
            data.append(';'.join('%s' % i for i in direction.estimates))
            table.add_row(data)
    print table

def current_routes(args):
    route_list = client.route_list(schedule=args.schedule,
                                   date=args.date)
    table = PrettyTable(["Name", "Number", "Color"])
    for route in route_list:
        table.add_row([route.name, route.number, route.color])
    print table

def route_info(args):
    route = client.route_info(args.route_number,
                              schedule=args.schedule,
                              date=args.date)
    table = PrettyTable(["Name", "Number", "Color"])
    table.add_row([route.name, route.number, route.color])
    print table

def station_list(_):
    stations = client.station_list()
    ordered_stations = [(k, stations[k]) for k in stations]
    ordered_stations.sort(key=lambda x: x[0])
    table = PrettyTable(["Abbreviation", "Name"])
    for item in ordered_stations:
        table.add_row([item[0], item[1]])
    print table

def station_info(args):
    station = client.station_info(args.station)
    print 'Station:', station.name
    print 'Address:', station.address, station.city, station.state
    print 'North Routes:', ';'.join('%s' % i for i in station.north_routes)
    print 'South Routes:', ';'.join('%s' % i for i in station.south_routes)

def station_access(args):
    station = client.station_access(args.station)
    print 'Station:', station.name
    print 'Entering:', station.entering
    print 'Exiting:', station.exiting

def station_schedule(args):
    station = client.station_schedule(args.station, date=args.date)
    print 'Station:', station.name
    table = PrettyTable(["Destination", "Origin Time", "Arrival Time"])
    for item in station.schedule_times:
        table.add_row([item.destination, item.origin_time.strftime('%H:%M'),
                       item.destination_time.strftime('%H:%M')])
    print table

def schedule_list(_):
    schedules = client.schedule_list()
    table = PrettyTable(["ID", "Effective Date"])
    for sched in schedules:
        table.add_row([sched.id, sched.effective_date])
    print table

def schedule_fare(args):
    fare = client.schedule_fare(args.origin_station,
                                args.destination_station,
                                schedule=args.schedule,
                                date=args.date)
    print 'Schedule Number:%s' % fare.schedule_number
    print 'Fare:%s' % fare.fare
    print 'Discount:%s' % fare.discount

def main():
    args = parse_args()
    # if no subcommand, make none
    try:
        MATCH[args.command][args.subcommand]
    except AttributeError:
        args.subcommand = None
    function = MATCH[args.command][args.subcommand]
    # call local function that matches name
    globals()[function](args)
