'''Use CLI Tool To Configure Shortcuts For Common Routes'''

import argparse
import json
import os
from prettytable import PrettyTable

from transit import client
from transit.common import utils
from transit.exceptions import TransitException

FUNCTION_MAPPING = {
    'leg' : {
        'create' : 'leg_create',
        'list' : 'leg_list',
        'delete' : 'leg_delete',
        'show' : 'leg_show',
    },
    'trip' : {
        'list' : 'trip_list',
        'create' : 'trip_create',
        'show' : 'trip_show',
        'delete' : 'trip_delete',
    },
}

HOME_PATH = os.path.expanduser('~') + '/.trip_planner'

def __create_directory(path):
    try:
        os.mkdir(path)
    except OSError as e:
        if 'File exists' in e:
            pass
        else:
            raise OSError(e)

def __ensure_directory(module):
    __create_directory(HOME_PATH)
    __create_directory(HOME_PATH + '/%s' % module)
    return os.listdir(HOME_PATH + '/%s' % module)

def __build_path(module, number):
    return HOME_PATH + '/%s/%s' % (module, number)

def parse_args():
    p = argparse.ArgumentParser(description='Trip Planner')

    subparsers = p.add_subparsers(dest='module', help='Module')

    leg = subparsers.add_parser('leg', help='Lget of a trip')
    leg_parsers = leg.add_subparsers(dest='command',
                                       help='Command')
    leg_createy = leg_parsers.add_parser('create',
                                           help='Create leg')
    leg_createy.add_argument('agency_tag',
                             help='actransit, bart, sf-muni, etc..')
    leg_createy.add_argument('stop_id',
                              help='ID of stop or station abbreviation')
    leg_createy.add_argument('--include', nargs='+',
                              help='Include destination or route tag')
    leg_parsers.add_parser('list', help='List legs')
    leg_deletey = leg_parsers.add_parser('delete', help='Delete Leg')
    leg_deletey.add_argument('id', type=int, help='Leg ID number')
    leg_showy = leg_parsers.add_parser('show', help='Show leg')
    leg_showy.add_argument('id', type=int, help='Leg ID number')

    trips = subparsers.add_parser('trip', help='Trip commands')
    trips_parsers = trips.add_subparsers(dest='command', help='Comand')
    trips_parsers.add_parser('list', help='List trips')
    trips_createy = trips_parsers.add_parser('create', help='Create trip')
    trips_createy.add_argument('name', help='Trip Name')
    trips_createy.add_argument('id', type=int, nargs='+', help='Leg IDs')
    trips_showy = trips_parsers.add_parser('show', help='Show trip')
    trips_showy.add_argument('id', help='Trip ID')
    trips_deletey = trips_parsers.add_parser('delete', help='Delete trip')
    trips_deletey.add_argument('id', help='Trip ID')

    return p.parse_args()

def __write_json(path, data):
    with open(path, 'w') as f:
        f.write(json.dumps(data, indent=4))

def __read_json(path):
    with open(path, 'r') as r:
        return json.loads(r.read())

def __validate_bart_station(stop_tag):
    # you can check the station list fairly quickly, since its hardcoded
    valid_stations = client.bart.station_list()
    if stop_tag.lower() not in [i for i in valid_stations]:
        raise TransitException('Bart station not valid:%s' % stop_tag)

def __validate_nextbus_stop(agency_tag, stop_id):
    # otherwise get a stop prediction now and check for errors
    try:
        predictions = client.nextbus.stop_prediction(agency_tag,
                                                     stop_id)
    except TransitException as e:
        raise TransitException("Could not identify stop:%s" % str(e))
    # here is the best time to get a route tag for the stop
    # this is the only way to get a stop tag, which is different than
    # .. the stop id used here. this is an intentional design because
    # .. the call used for getting a single stop prediction uses stop id
    # .. while the prediction method for multiple stops at a time uses
    # .. the stop tag
    # using multiple stops is a good way of saving time by elimating
    # .. the need for multiple calls to the nextbus api
    print 'finding stop tag for agency:%s and stop id:%s' % \
        (agency_tag, stop_id)
    # use first predictions route tag
    route_tag = predictions[0].route_tag
    route = client.nextbus.route_get(agency_tag, route_tag)
    stop_tag = None
    stop_title = None
    stop_id = int(stop_id)
    for i in route.stops:
        if i.stop_id == stop_id:
            stop_tag = i.tag
            stop_title = i.title
            break
    # also return a list of all possible route_tags from predictions
    # .. this is also needed for the multiple stop logic later
    route_tags = [i.route_tag for i in predictions]
    return stop_tag, stop_title, route_tags

def leg_create(args):
    if args.agency_tag.lower() == 'bart':
        __validate_bart_station(args.stop_id)
        stop_tag = None
        route_tags = args.include
        stop_title = client.bart.station_list()[args.stop_id.lower()]
    else:
        stop_tag, stop_title, route_tags = __validate_nextbus_stop(args.agency_tag,
                                                       args.stop_id)
        # if nextbus, if no args.include given, default to route tags
        # .. this is for http speed up logic later
        if args.include:
            route_tags = args.include
        else:
            print 'No route tags given, so defaulting to:%s' % \
                ', '.join(i for i in route_tags)
    # should be good from here, add to rest
    files = __ensure_directory('legs')
    try:
        new_number = max([int(i) for i in files]) + 1
    except ValueError:
        new_number = 0
    data = {
        'id' : new_number,
        'agency' :  args.agency_tag,
        'stop_id' : args.stop_id,
        'include' : route_tags,
        'stop_tag' : stop_tag,
        'stop_title' : stop_title,
    }
    __write_json(__build_path('legs', new_number), data)
    print 'Created leg:', new_number

def leg_list(_):
    files = __ensure_directory('legs')
    table = PrettyTable(["Leg ID", "Agency", "Stop ID", "Stop Tag", "Stop Title",
                         "Routes/Directions"])
    table_data = []
    for f in files:
        data = __read_json(__build_path('legs', f))
        try:
            include_data = ', '.join(i for i in data['include'])
        except TypeError:
            include_data = ''
        table_data.append([data['id'], data['agency'], data['stop_id'],
                           data['stop_tag'], data['stop_title'], include_data])
    table_data.sort(key=lambda x: x[0])
    for row in table_data:
        table.add_row(row)
    print table

def leg_delete(args):
    files = __ensure_directory('legs')
    if args.id not in [int(i) for i in files]:
        raise TransitException("Invalid Leg ID:%s" % args.id)
    os.remove(__build_path('legs', args.id))
    print 'Deleted Leg:', args.id

def __show_bart_leg(estimations):
    table = PrettyTable(["Station", "Direction", "Estimates(minutes)"])
    for est in estimations:
        for direct in est.directions:
            preds = ' ; '.join('%d' % i.minutes for i in direct.estimates)
            table.add_row([est.name, direct.name, preds])
    print table

def __show_nextbus_leg(estimations):
    table = PrettyTable(["Route", "Stop Title",
                         "Direction", "Predictions"])
    for est in estimations:
        data = []
        data += [est.route_title, est.stop_title]
        for direct in est.directions:
            data += [direct.title]
            preds = ' ; '.join(utils.pretty_time(i.minutes,
                                                 i.seconds - (i.minutes * 60))\
                for i in direct.predictions)
            data += [preds]
            table.add_row(data)
    print table

def leg_show(args):
    files = __ensure_directory('legs')
    if args.id not in [int(i) for i in files]:
        raise TransitException("Invalid Leg ID:%s" % args.id)
    data = __read_json(__build_path('legs', args.id))
    print 'Agency:', data['agency']
    print 'Stop ID:', data['stop_id']
    if data['agency'] == 'bart':
        estimations = client.bart.station_departures(data['stop_id'],
                                                     destinations=data['include'])
        __show_bart_leg(estimations)
    else:
        estimations = client.nextbus.stop_prediction(data['agency'],
                                                     data['stop_id'],
                                                     data['include'],)
        __show_nextbus_leg(estimations)

def trip_create(args):
    files = __ensure_directory('trips')
    if args.name.lower() in [i.lower() for i in files]:
        raise TransitException("Invalid name, already in use:%s" % args.name)
    trip_ids = []
    for f in files:
        data = __read_json(__build_path('trips', f))
        trip_ids.append(data['id'])
    try:
        max_id = max(trip_ids)
    except ValueError:
        max_id = -1
    valid_legs = [int(i) for i in __ensure_directory('legs')]
    for leg in args.id:
        if leg not in valid_legs:
            raise TransitException("Leg cannot be found:%s" % leg)
    data = {
        'id' : max_id + 1,
        'name' : args.name,
        'legs' : args.id,
    }
    __write_json(__build_path('trips', data['id']), data)
    print 'Trip Created:', args.name

def trip_list(_):
    files = __ensure_directory('trips')
    table = PrettyTable(["ID", "Name", "Legs"])
    for f in files:
        data = __read_json(__build_path('trips', f))
        table.add_row([data['id'],
                       data['name'],
                       ','.join('%s' % i for i in data['legs'])])
    print table

def trip_show(args):
    files = __ensure_directory('trips')
    if args.id not in [i for i in files]:
        raise TransitException("Invalid name, cannot find:%s" % args.id)
    trip_data = __read_json(__build_path('trips', args.id))

    nextbus_leg_data = {}
    station_data = {}
    for leg in trip_data['legs']:
        leg_data = __read_json(__build_path('legs', leg))
        if leg_data['agency'] == 'bart':
            station_data[leg_data['stop_id']] = leg_data['include']
        else:
            nextbus_leg_data.setdefault(leg_data['agency'], {})
            agency_data = nextbus_leg_data[leg_data['agency']]
            for route in leg_data['include']:
                agency_data.setdefault(route, [])
                agency_data[route].append(leg_data['stop_tag'])
    if station_data:
        print 'Bart data'
        estimates = client.bart.multiple_station_departures(station_data)
        __show_bart_leg(estimates)
    for agency, data in nextbus_leg_data.iteritems():
        print 'Nextbus Agency:%s' % agency
        estimates = client.nextbus.multiple_stop_predictions(agency,
                                                             data)
        __show_nextbus_leg(estimates)

def trip_delete(args):
    files = __ensure_directory('trips')
    if args.id not in [i for i in files]:
        raise TransitException("Invalid name, cannot find:%s" % args.id)
    os.remove(__build_path('trips', args.id))
    print 'Deleted trip:%s' % args.id

def main():
    args = parse_args()
    method = globals()[FUNCTION_MAPPING[args.module][args.command]]
    method(args)
