import logging

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import UnmappedInstanceError

from transit.modules.bart import client as bart_client
from transit.modules.nextbus import client as nextbus_client
from planner.exceptions import TripPlannerException

Base = declarative_base()

log = logging.getLogger(__name__)

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

def clean_sql(sql_object):
    new_data = {}
    data = sql_object.__dict__
    for key in data.keys():
        if key.startswith("_"):
            continue
        if isinstance(data[key], unicode):
            new_data[key] = data[key].encode('utf-8')
        else:
            new_data[key] = data[key]
    return new_data

# TODO planner functions should assert inputs
class TripPlanner(object):
    def __init__(self, engine):
        Base.metadata.create_all(engine)
        Base.metadata.bind = engine
        self.db_session = sessionmaker(bind=engine)()

    def __validate_bart_station(self, stop_tag, include): #pylint: disable=no-self-use
        # you can check the station list fairly quickly, since its hardcoded
        valid_stations = bart_client.station_list()
        if stop_tag.lower() not in [i for i in valid_stations]:
            raise TripPlannerException('Bart station not valid:%s' % stop_tag)

        # TODO this should check destinations are valid if not None
        if not include:
            # check for all possible routes from station
            # use this to get a list of all possible destinations
            station = bart_client.station_info(stop_tag.lower())
            all_routes = set(station['north_routes'] + station['south_routes'])
            destinations = set([])
            for route in all_routes:
                r = bart_client.route_info(route)
                destinations.add(r['destination'].lower())
            include = list(destinations)
        return valid_stations[stop_tag], include

    def __validate_nextbus_stop(self, agency_tag, stop_id, includes):
        try:
            predictions = nextbus_client.stop_prediction(agency_tag,
                                                         stop_id)
        except TripPlannerException as e:
            raise TripPlannerException("Could not identify stop:%s" % str(e))

        # here is the best time to get a route tag for the stop
        # this is the only way to get a stop tag, which is different than
        # .. the stop id used here. this is an intentional design because
        # .. the call used for getting a single stop prediction uses stop id
        # .. while the prediction method for multiple stops at a time uses
        # .. the stop tag
        # using multiple stops is a good way of saving time by elimating
        # .. the need for multiple calls to the nextbus api
        try:
            leg = self.db_session.query(Leg).\
                filter(Leg.stop_id == stop_id).\
                filter(Leg.agency == agency_tag)[0]
            stop_tag = leg.stop_tag.encode('utf-8')
            stop_title = leg.stop_title.encode('utf-8')
            stop_id = stop_id.encode('utf-8')
        except IndexError:
            # use first predictions route tag
            route_tag = predictions[0]['route_tag']
            route = nextbus_client.route_get(agency_tag, route_tag)
            stop_tag = None
            stop_title = None
            stop_id = stop_id
            for stop in route['stops']:
                if stop['stop_id'] == stop_id:
                    stop_tag = stop['stop_tag']
                    stop_title = stop['title']
                    break
        # also return a list of all possible route_tags from predictions
        # .. this is also needed for the multiple stop logic later
        # TODO to some verification that the route tags are valid
        route_tags = includes
        if route_tags and not isinstance(route_tags, list):
            route_tags = [route_tags]
        if not route_tags:
            route_tags = ['%s' % i['route_tag']for i in predictions]
        return stop_tag, stop_title, route_tags

    def leg_create(self, agency_tag, stop_id, include=None):
        log.info("Creating leg for agency:%s, stop:%s, including:%s",
                 agency_tag, stop_id, include)
        if agency_tag == 'bart':
            stop_title, route_tags = self.__validate_bart_station(stop_id,
                                                                  include)
            stop_tag = None
        else:
            stop_tag, stop_title, route_tags = \
                self.__validate_nextbus_stop(agency_tag,
                                             stop_id,
                                             include)
        # Add new leg object
        stop_id = ('%s' % stop_id).decode('utf-8')
        stop_tag = ('%s' % stop_tag).decode('utf-8')
        stop_title = ('%s' % stop_title).decode('utf-8')
        agency = ('%s' % agency_tag).decode('utf-8')
        new_leg = Leg(stop_id=stop_id,
                      stop_tag=stop_tag,
                      stop_title=stop_title,
                      agency=agency)
        self.db_session.add(new_leg)
        self.db_session.commit()

        # Add all routes in leg includes
        route_tags = route_tags or []
        for tag in route_tags:
            cleaned_tag = ('%s' % tag).decode('utf-8')
            leg_include = LegInclude(leg_id=new_leg.id,
                                     tag=cleaned_tag)
            self.db_session.add(leg_include)
        self.db_session.commit()

        # refresh here for better return
        new_leg = self.db_session.query(Leg).get(new_leg.id)
        leg = clean_sql(new_leg)
        leg['includes'] = route_tags
        return leg

    def leg_list(self):
        log.info("Grabbing list of all legs")
        legs = []
        all_legs = self.db_session.query(Leg).all()
        for leg in all_legs:
            leg_cleaned = clean_sql(leg)
            leg_cleaned['includes'] = []
            includes = self.db_session.query(LegInclude).\
                filter(LegInclude.leg_id == leg.id)
            for leg_include in includes:
                leg_cleaned['includes'].append(leg_include.tag.encode('utf-8'))
            legs.append(leg_cleaned)
        log.info("Legs:%s", legs)
        return legs

    def leg_delete(self, leg_id):
        log.info("Deleting Leg:%s", leg_id)
        trip_legs = self.db_session.query(TripLeg).\
            filter(TripLeg.leg_id == leg_id)
        for leg in trip_legs:
            raise TripPlannerException('Cannot delete leg, '
                                       'being used by a Trip:%s' % leg.trip_id)
        log.debug("Deleting all leg includes")
        self.db_session.query(LegInclude).\
            filter(LegInclude.leg_id == leg_id).delete()
        self.db_session.commit()

        log.debug("Now deleting leg object:%s", leg_id)
        leg = self.db_session.query(Leg).get(leg_id)
        if not leg:
            raise TripPlannerException("No leg with this ID:%s" % leg_id)
        self.db_session.delete(leg)
        self.db_session.commit()
        return True

    def leg_show(self, leg_id):
        log.info("Grabbing web data for leg:%s", leg_id)
        leg = self.db_session.query(Leg).get(leg_id)
        if not leg:
            raise TripPlannerException("No Leg with this ID:%s" % leg_id)
        includes = [include.tag.encode('utf-8') for include in self.db_session.query(LegInclude).\
            filter(LegInclude.leg_id == leg_id)]
        preds = None
        if leg.agency == 'bart':
            preds = bart_client.station_departures(leg.stop_id.encode('utf-8'),
                                                   destinations=includes)
        else:
            preds = nextbus_client.stop_prediction(leg.agency.encode('utf-8'),
                                                   leg.stop_id.encode('utf-8'),
                                                   route_tags=includes)
        log.info("Found preds:%s", preds)
        return leg.agency, preds

    def trip_create(self, name, legs):
        new_trip = Trip(name=name.decode('utf-8'))
        self.db_session.add(new_trip)
        self.db_session.commit()

        if not isinstance(legs, list):
            legs = [legs]
        elif legs is None:
            legs = []

        for leg in legs:
            new_leg = TripLeg(trip_id=new_trip.id,
                              leg_id=leg)
            self.db_session.add(new_leg)
        self.db_session.commit()

        new_trip = self.db_session.query(Trip).get(new_trip.id)
        return clean_sql(new_trip)

    def trip_list(self):
        trips = {}
        all_trips = self.db_session.query(Trip).all()
        for trip in all_trips:
            clean_trip = clean_sql(trip)
            trip_id = clean_trip.pop('id')
            trips[trip_id] = clean_trip
            trips[trip_id]['legs'] = []
            legs = self.db_session.query(TripLeg).\
                filter(TripLeg.trip_id == trip_id)
            for trip_leg in legs:
                trips[trip_id]['legs'].append(trip_leg.leg_id)
        return trips

    def trip_show(self, trip_id):
        try:
            self.db_session.query(Trip).get(trip_id)
        except UnmappedInstanceError:
            raise TripPlannerException("No Trip with ID:%s" % trip_id)
        nextbus_data = {}
        station_data = {}

        legs = self.db_session.query(TripLeg).\
            filter(TripLeg.trip_id == trip_id)

        for trip_leg in legs:
            includes = self.db_session.query(LegInclude).\
                filter(LegInclude.leg_id == trip_leg.leg_id)
            leg = self.db_session.query(Leg).get(trip_leg.leg_id)
            if leg.agency == 'bart':
                station_data.setdefault(leg.stop_id, [])
                for leg_include in includes:
                    station_data[leg.stop_id].append(leg_include.tag)
            else:
                agency = leg.agency.encode('utf-8')
                nextbus_data.setdefault(agency, {})

                for leg_include in includes:
                    leg_tag = leg_include.tag.encode('utf-8')
                    stop_tag = leg.stop_tag.encode('utf-8')
                    nextbus_data[agency].setdefault(leg_tag, [])
                    nextbus_data[agency][leg_tag].append(stop_tag)
        trip_data = {
            'bart' : None,
            'nextbus' : {},
        }
        if station_data:
            trip_data['bart'] = bart_client.station_multiple_departures(station_data)
        for agency, data in nextbus_data.iteritems():
            trip_data['nextbus'][agency] = nextbus_client.stop_multiple_predictions(agency,
                                                                                    data)
        return trip_data

    def trip_delete(self, trip_id):
        try:
            trip = self.db_session.query(Trip).get(trip_id)
            self.db_session.delete(trip)
            self.db_session.commit()
        except UnmappedInstanceError:
            raise TripPlannerException("No Trip with ID:%s" % trip_id)

        # Delete all trip legs associated
        legs = self.db_session.query(TripLeg).\
            filter(TripLeg.trip_id == trip_id)
        for leg in legs:
            self.db_session.delete(leg)
        self.db_session.commit()

        return True
