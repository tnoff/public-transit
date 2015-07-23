'''Use CLI Tool To Configure Shortcuts For Common Routes'''

import argparse
import os
from prettytable import PrettyTable
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import UnmappedInstanceError

from transit.modules.bart import client as bart_client
from transit.modules.nextbus import client as nextbus_client
from transit.modules.nextbus import utils
from transit.exceptions import TransitException

Base = declarative_base()

class Leg(Base): #pylint:disable=no-init
    __tablename__ = 'leg'
    id = Column(Integer, primary_key=True)
    agency = Column(String(128))
    stop_id = Column(String(64))
    stop_tag = Column(String(64))
    stop_title = Column(String(128))

class LegInclude(Base): #pylint:disable=no-init
    __tablename__ = 'leg_include'
    id = Column(Integer, primary_key=True)
    leg_id = Column(Integer, ForeignKey('leg.id'))
    tag = Column(String(64))

class Trip(Base): #pylint:disable=no-init
    __tablename__ = 'trip'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))

class TripLeg(Base): #pylint:disable=no-init
    __tablename__ = 'trip_leg'
    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trip.id'))
    leg_id = Column(Integer, ForeignKey('leg.id'))

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
    trips_createy.add_argument('leg_id', type=int, nargs='+', help='Leg IDs')
    trips_showy = trips_parsers.add_parser('show', help='Show trip')
    trips_showy.add_argument('id', help='Trip ID')
    trips_deletey = trips_parsers.add_parser('delete', help='Delete trip')
    trips_deletey.add_argument('id', help='Trip ID')

    return p.parse_args()

def __validate_bart_station(stop_tag):
    # you can check the station list fairly quickly, since its hardcoded
    valid_stations = bart_client.station_list()
    if stop_tag.lower() not in [i for i in valid_stations]:
        raise TransitException('Bart station not valid:%s' % stop_tag)

def __validate_nextbus_stop(agency_tag, stop_id):
    # otherwise get a stop prediction now and check for errors
    try:
        predictions = nextbus_client.stop_prediction(agency_tag,
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
    route = nextbus_client.route_get(agency_tag, route_tag)
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

def leg_create(args, db_session):
    if args.agency_tag.lower() == 'bart':
        __validate_bart_station(args.stop_id)
        stop_tag = None
        route_tags = args.include
        stop_title = bart_client.station_list()[args.stop_id.lower()]
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
    new_leg = Leg(stop_id=args.stop_id,
                  stop_tag=stop_tag,
                  stop_title=stop_title,
                  agency=args.agency_tag.lower(),)
    db_session.add(new_leg)
    db_session.commit()

    if route_tags is None:
        route_tags = []
    for tag in route_tags:
        leg_include = LegInclude(leg_id=new_leg.id,
                                 tag=tag)
        db_session.add(leg_include)
    db_session.commit()
    print 'Created leg:', new_leg.id

def leg_list(_, db_session):
    table = PrettyTable(["Leg ID", "Agency", "Stop ID", "Stop Tag", "Stop Title",
                         "Routes/Directions"])
    table_data = []
    for leg in db_session.query(Leg):
        data = [leg.id, leg.agency, leg.stop_id, leg.stop_tag, leg.stop_title]
        leg_includes = db_session.query(LegInclude).filter_by(leg_id=leg.id)
        routes = ', '.join(i.tag for i in leg_includes)
        data.append(routes)
        table_data.append(data)
    table_data.sort(key=lambda x: x[0])
    for row in table_data:
        table.add_row(row)
    print table

def leg_delete(args, db_session):
    leg = db_session.query(Leg).get(args.id)
    try:
        db_session.delete(leg)
        db_session.commit()
        print 'Deleted Leg:', args.id
    except UnmappedInstanceError:
        print 'Cannot delete leg:%s' % args.id

    for includes in db_session.query(LegInclude).filter_by(leg_id=args.id):
        db_session.delete(includes)
    db_session.commit()

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

def leg_show(args, db_session):
    try:
        leg = db_session.query(Leg).get(args.id)
    except UnmappedInstanceError:
        print 'Cannot find leg:%s' % args.id
        return
    print 'Agency:', leg.agency
    print 'Stop ID:', leg.stop_id
    tags = [i.tag for i in db_session.query(LegInclude).filter_by(leg_id=args.id)]
    if leg.agency == 'bart':
        estimations = bart_client.station_departures(leg.stop_id,
                                                     destinations=tags,)
        __show_bart_leg(estimations)
    else:
        estimations = nextbus_client.stop_prediction(leg.agency,
                                                     leg.stop_id,
                                                     tags,)
        __show_nextbus_leg(estimations)

def trip_create(args, db_session):
    new_trip = Trip(name=args.name)
    db_session.add(new_trip)
    db_session.commit()

    for leg in args.leg_id:
        new_leg = TripLeg(trip_id=new_trip.id,
                          leg_id=leg)
        db_session.add(new_leg)
    db_session.commit()
    print 'Trip Created:', new_trip.id

def trip_list(_, db_session):
    table = PrettyTable(["ID", "Name", "Legs"])
    data = []
    for trip in db_session.query(Trip):
        legs = db_session.query(TripLeg).filter_by(trip_id=trip.id)
        data.append([trip.id,
                     trip.name,
                     ', '.join('%d' % i.leg_id for i in legs)])
    data.sort(key=lambda x: x[0])
    for row in data:
        table.add_row(row)
    print table

def trip_show(args, db_session):
    nextbus_leg_data = {}
    station_data = {}
    try:
        legs = db_session.query(TripLeg).filter_by(trip_id=args.id)
    except UnmappedInstanceError:
        print 'Cannot find legs for trip:%s' % args.id
        return
    for leg in legs:
        leg = db_session.query(Leg).get(leg.leg_id)
        tags = [i.tag for i in db_session.query(LegInclude).filter_by(leg_id=leg.id)]
        if leg.agency == 'bart':
            station_data[leg.stop_id] = tags
        else:
            nextbus_leg_data.setdefault(leg.agency, {})
            agency_data = nextbus_leg_data[leg.agency]
            for route in tags:
                agency_data.setdefault(route, set([]))
                agency_data[route].add(leg.stop_tag)
    if station_data:
        print 'Bart data'
        estimates = bart_client.multiple_station_departures(station_data)
        __show_bart_leg(estimates)
    for agency, data in nextbus_leg_data.iteritems():
        print 'Nextbus Agency:%s' % agency
        estimates = nextbus_client.multiple_stop_predictions(agency,
                                                             data)
        __show_nextbus_leg(estimates)

def trip_delete(args, db_session):
    try:
        trip = db_session.query(Trip).get(args.id)
        db_session.delete(trip)
        db_session.commit()
    except UnmappedInstanceError:
        print 'Cannot delete trip:%s' % args.id
        return
    for leg in db_session.query(TripLeg).filter_by(trip_id=args.id):
        db_session.delete(leg)
    db_session.commit()
    print 'Deleted trip:%s' % args.id

def main():
    args = parse_args()
    __create_directory(HOME_PATH)
    engine = create_engine('sqlite:///' + HOME_PATH + '/sqlite.sql')
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    db_session = sessionmaker(bind=engine)()
    method = globals()[FUNCTION_MAPPING[args.module][args.command]]
    method(args, db_session)
