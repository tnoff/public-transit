import argparse
import os
from prettytable import PrettyTable

from trip_planner import utils
from trip_planner.client import TripPlanner
from transit.exceptions import TransitException
from transit.modules.nextbus import utils as bus_utils

HOME_PATH = os.path.expanduser('~') + '/.trip_planner'

def __create_directory(path):
    try:
        os.mkdir(path)
    except OSError as e:
        if 'File exists' in e:
            pass
        else:
            raise OSError(e)

def parse_args():
    p = argparse.ArgumentParser(description='Trip Planner')

    subparsers = p.add_subparsers(dest='module', help='Module')

    leg = subparsers.add_parser('leg', help='Let of a trip')
    leg_parsers = leg.add_subparsers(dest='command',
                                     help='Command')
    leg_createy = leg_parsers.add_parser('create',
                                         help='Create leg')
    leg_createy.add_argument('agency_tag',
                             help='actransit, bart, sf-muni, etc..')
    leg_createy.add_argument('stop_id',
                             help='ID of stop or station abbreviation')
    leg_createy.add_argument('--destinations', nargs='+',
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
    trips_createy.add_argument('leg', type=int, nargs='+', help='Leg IDs')
    trips_showy = trips_parsers.add_parser('show', help='Show trip')
    trips_showy.add_argument('id', type=int, help='Trip ID')
    trips_deletey = trips_parsers.add_parser('delete', help='Delete trip')
    trips_deletey.add_argument('id', type=int, help='Trip ID')

    return p.parse_args()

def leg_create(args, trip_planner):
    agency_tag = args.agency_tag.lower()
    stop_id = args.stop_id.lower()
    new_leg = trip_planner.leg_create(agency_tag, stop_id,
                                      destinations=args.destinations)
    print 'New leg created:', new_leg['id']

def leg_list(_, trip_planner):
    legs = trip_planner.leg_list()
    table = PrettyTable(["Leg ID", "Agency", "Stop ID", "Stop Title",
                         "Routes/Directions"])
    for leg_data in legs:
        table.add_row([leg_data['id'], leg_data['agency'],
                       leg_data['stop_id'], leg_data['stop_title'],
                       ' ; '.join(i for i in leg_data['includes'])])
    print table

def __nice_predictions(predictions):
    preds = []
    for pred in predictions:
        minutes = int(pred['minutes'])
        seconds = int(pred['seconds'])
        preds.append(bus_utils.prediction_time(minutes, seconds))
    return ' ; '.join(i for i in preds)

def __bart_leg(estimates):
    table = PrettyTable(["Station", "Direction", "Estimates(minutes)"])
    for est in estimates:
        for direct in est['directions']:
            preds = ' ; '.join('%s' % i['minutes'] for i in direct['estimates'])
            table.add_row([est['name'], direct['name'], preds])
    return table

def __nextbus_leg(estimates):
    table = PrettyTable(["Route", "Stop Title",
                         "Direction", "Predictions"])
    for est in estimates:
        base_data = [est['route_title'], est['stop_title']]
        for direct in est['directions']:
            data = base_data + [direct['title']]
            data.append(__nice_predictions(direct['predictions']))
            table.add_row(data)
    return table

def leg_show(args, trip_planner):
    try:
        agency, estimations = trip_planner.leg_show(args.id) #pylint: disable=unpacking-non-sequence
    except TransitException as e:
        print 'ERROR:', str(e)
        return
    if agency == 'bart':
        table = __bart_leg(estimations)
    else:
        table = __nextbus_leg(estimations)
    print table

def leg_delete(args, trip_planner):
    try:
        deleted = trip_planner.leg_delete(args.id)
        if deleted:
            print 'Deleted leg id:%s' % args.id
    except TransitException as t:
        print '%s' % t

def trip_create(args, trip_planner):
    new_trip = trip_planner.trip_create(args.name, args.leg)
    print 'Trip created:%s' % new_trip['id']

def trip_list(_, trip_planner):
    trips = trip_planner.trip_list()
    table = PrettyTable(["ID", "Name", "Legs"])
    for trip_data in trips:
        table.add_row([trip_data['id'], trip_data['name'],
                       ' ; '.join('%s' % i for i in trip_data['legs'])])
    print table

def trip_delete(args, trip_planner):
    try:
        deleted = trip_planner.trip_delete(args.id)
        if deleted:
            print 'Deleted trip id:%s' % args.id
    except TransitException as t:
        print '%s' % t

def trip_show(args, trip_planner):
    try:
        trip_data = trip_planner.trip_show(args.id)
    except TransitException as t:
        print '%s' % t
        return
    if trip_data['bart']:
        print 'Bart'
        print __bart_leg(trip_data['bart'])
    for agency, estimates in trip_data['nextbus'].iteritems():
        print agency
        print __nextbus_leg(estimates)

FUNCTION_MAPPING = {
    'leg' : {
        'create' : leg_create,
        'list' : leg_list,
        'delete' : leg_delete,
        'show' : leg_show,
    },
    'trip' : {
        'list' : trip_list,
        'create' : trip_create,
        'show' : trip_show,
        'delete' : trip_delete,
    },
}

def main():
    args = parse_args()
    __create_directory(HOME_PATH)
    db_name = HOME_PATH + '/trip_db.sql'
    engine = utils.database_engine(db_name)
    planner = TripPlanner(engine)
    method = FUNCTION_MAPPING[args.module][args.command]
    method(args, planner)
