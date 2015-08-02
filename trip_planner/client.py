'''Use CLI Tool To Configure Shortcuts For Common Routes'''

from collections import OrderedDict

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import UnmappedInstanceError

from transit.modules.bart import client as bart_client
from transit.modules.nextbus import client as nextbus_client
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

class TripPlanner(object):
    def __init__(self, engine):
        Base.metadata.create_all(engine)
        Base.metadata.bind = engine
        self.db_session = sessionmaker(bind=engine)()

    def __validate_bart_station(self, stop_tag): #pylint: disable=no-self-use
        # you can check the station list fairly quickly, since its hardcoded
        valid_stations = bart_client.station_list()
        if stop_tag.lower() not in [i for i in valid_stations]:
            raise TransitException('Bart station not valid:%s' % stop_tag)
        return valid_stations[stop_tag]

    def __validate_nextbus_stop(self, agency_tag, stop_id, includes=None):
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
        # first check if in db
        try:
            leg = self.db_session.query(Leg).filter(Leg.stop_id == stop_id)[0]
            stop_tag = leg.stop_tag
            stop_title = leg.stop_title
            stop_id = int(stop_id)
        except IndexError:
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
        route_tags = includes
        if not route_tags:
            route_tags = [i.route_tag for i in predictions]
        return stop_tag, stop_title, route_tags

    def leg_create(self, agency_tag, stop_id, include=None):
        if agency_tag == 'bart':
            stop_title = self.__validate_bart_station(stop_id)
            stop_tag = None
            route_tags = include
        else:
            stop_tag, stop_title, route_tags = self.__validate_nextbus_stop(agency_tag,
                                                                            stop_id,
                                                                            includes=include)
        # Add new leg object
        new_leg = Leg(stop_id=stop_id,
                      stop_tag=stop_tag,
                      stop_title=stop_title,
                      agency=agency_tag)
        self.db_session.add(new_leg)
        self.db_session.commit()

        # Add all routes in leg includes
        if route_tags:
            for tag in route_tags:
                leg_include = LegInclude(leg_id=new_leg.id,
                                         tag=tag.lower())
                self.db_session.add(leg_include)
            self.db_session.commit()
        return new_leg

    def leg_list(self):
        legs = OrderedDict()
        _legs = self.db_session.query(Leg, LegInclude).\
            join(LegInclude, Leg.id == LegInclude.leg_id)
        # format returned in will be
        # .. [(Leg1, LegInclude1), (Leg1, LegInclude2), (Leg2, LegIncludeN), ...]
        for result in _legs:
            leg, leg_include = result[0], result[1]
            try:
                legs[leg.id]
            except KeyError:
                legs[leg.id] = {
                    'agency' : leg.agency,
                    'stop_id' : leg.stop_id,
                    'stop_tag' : leg.stop_tag,
                    'stop_title' : leg.stop_title,
                }
            legs[leg.id].setdefault('includes', [])
            legs[leg.id]['includes'].append(leg_include.tag)
        return legs

    def leg_delete(self, leg_id):
        # Check if being used by any trips
        trip_legs = self.db_session.query(Trip, TripLeg).\
            join(TripLeg, TripLeg.trip_id == Trip.id).\
            filter(TripLeg.leg_id == leg_id)
        for result in trip_legs:
            trip = result[0]
            raise TransitException('Cannot delete leg, '
                                   'being used by a Trip:%s' % trip.id)
        try:
            leg = self.db_session.query(Leg).get(leg_id)
            self.db_session.delete(leg)
            for includes in self.db_session.query(LegInclude).\
                                                 filter_by(leg_id=leg_id):
                self.db_session.delete(includes)
            self.db_session.commit()
        except UnmappedInstanceError:
            raise TransitException("No leg with this ID:%s" % leg_id)
        return True

    def leg_show(self, leg_id):
        _leg = self.db_session.query(Leg, LegInclude).\
            filter(Leg.id == leg_id).\
            filter(LegInclude.leg_id == leg_id)
        # Since leg should be the same for all results, take first one
        # .. then build out tags with the rest
        try:
            leg = _leg[0][0]
        except IndexError:
            raise TransitException("No Leg with ID:%s" % leg_id)
        includes = [i[1].tag for i in _leg]
        if leg.agency == 'bart':
            return leg.agency, bart_client.station_departures(leg.stop_id,
                                                              destinations=includes,)
        else:
            return leg.agency, nextbus_client.stop_prediction(leg.agency,
                                                              leg.stop_id,
                                                              includes,)
    def trip_create(self, name, legs):
        new_trip = Trip(name=name)
        self.db_session.add(new_trip)
        self.db_session.commit()

        for leg in legs:
            new_leg = TripLeg(trip_id=new_trip.id,
                              leg_id=leg)
            self.db_session.add(new_leg)
        self.db_session.commit()
        return new_trip

    def trip_list(self):
        trips = OrderedDict()
        _trips = self.db_session.query(Trip, TripLeg).\
            join(TripLeg, TripLeg.trip_id == Trip.id)
        for result in _trips:
            trip, trip_leg = result[0], result[1]
            try:
                trips[trip.id]
            except KeyError:
                trips[trip.id] = {
                    'name' : trip.name
                }
            trips[trip.id].setdefault('legs', [])
            trips[trip.id]['legs'].append(trip_leg.leg_id)
        return trips

    def trip_show(self, trip_id):
        _trip = self.db_session.query(TripLeg, Leg, LegInclude).\
            join(Leg, TripLeg.leg_id == Leg.id).\
            join(LegInclude, LegInclude.leg_id == Leg.id).\
            filter(TripLeg.trip_id == trip_id)
        try:
            _trip[0]
        except IndexError:
            raise TransitException("No Trip with ID:%s" % trip_id)
        nextbus_data = {}
        station_data = {}
        for result in _trip:
            leg, leg_include = result[1], result[2]
            if leg.agency == 'bart':
                station_data.setdefault(leg.stop_id, [])
                station_data[leg.stop_id].append(leg_include.tag)
            else:
                nextbus_data.setdefault(leg.agency, {})
                agency_data = nextbus_data[leg.agency]
                agency_data.setdefault(leg_include.tag, [])
                agency_data[leg_include.tag].append(leg.stop_tag)
        trip_data = {
            'bart' : None,
            'nextbus' : {},
        }
        if station_data:
            trip_data['bart'] = bart_client.multiple_station_departures(station_data)
        for agency, data in nextbus_data.iteritems():
            trip_data['nextbus'][agency] = nextbus_client.multiple_stop_predictions(agency,
                                                                                    data)
        return trip_data

    def trip_delete(self, trip_id):
        try:
            trip = self.db_session.query(Trip).get(trip_id)
            self.db_session.delete(trip)
            for leg in self.db_session.query(TripLeg).filter_by(trip_id=trip_id):
                self.db_session.delete(leg)
            self.db_session.commit()
        except UnmappedInstanceError:
            raise TransitException("No Trip with ID:%s" % trip_id)
        return True
