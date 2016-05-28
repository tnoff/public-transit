from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import UnmappedInstanceError

from transit import bart as bart_client
from transit import nextbus as nextbus_client
from trip_planner.exceptions import TripPlannerException

Base = declarative_base()

class Leg(Base): #pylint:disable=no-init
    __tablename__ = 'leg'
    id = Column(Integer, primary_key=True)
    agency = Column(String(128))
    stop_id = Column(String(64))
    stop_tag = Column(String(64))
    stop_title = Column(String(128))

class LegDestination(Base): #pylint:disable=no-init
    __tablename__ = 'leg_destination'
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

class TripPlanner(object):
    def __init__(self, database_engine):
        Base.metadata.create_all(database_engine)
        Base.metadata.bind = database_engine
        self.db_session = sessionmaker(bind=database_engine)()

    def __validate_bart_station(self, stop_tag, include): #pylint: disable=no-self-use
        # you can check the station list fairly quickly, since its hardcoded
        valid_stations = bart_client.station_list()
        if stop_tag.lower() not in [i for i in valid_stations]:
            raise TripPlannerException('Bart station not valid:%s' % stop_tag)

        # check for all possible routes from station
        # use this to get a list of all possible destinations
        station = bart_client.station_info(stop_tag.lower())
        all_routes = set(station['north_routes'] + station['south_routes'])
        destinations = set([])
        for route in all_routes:
            r = bart_client.route_info(route)
            destinations.add(r['destination'].lower())
        possible_destinations = list(destinations)
        if include:
            if not isinstance(include, list):
                include = [include]
            for destination in include:
                if destination not in possible_destinations:
                    raise TripPlannerException("Invalid destination:%s" % destination)
        else:
            include = possible_destinations
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
        possible_routes = [route['route_tag'] for route in predictions]
        try:
            leg = self.db_session.query(Leg).\
                filter(Leg.stop_id == stop_id).\
                filter(Leg.agency == agency_tag)[0]
            stop_tag = leg.stop_tag.encode('utf-8')
            stop_title = leg.stop_title.encode('utf-8')
            stop_id = stop_id.encode('utf-8')
        except IndexError:
            # use first predictions route tag
            route_tag = possible_routes[0]
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
        route_tags = includes
        if route_tags and not isinstance(route_tags, list):
            route_tags = [route_tags]
        if not route_tags:
            route_tags = possible_routes
        else:
            for route in route_tags:
                if route not in possible_routes:
                    raise TripPlannerException("Invalid route given:%s" % route)
        return stop_tag, stop_title, route_tags

    def leg_create(self, agency_tag, stop_id, destinations=None):
        '''Create a new leg with a given stop id and includes
           agency_tag : agency tag
           stop_id : identifier of stop
           include: include only destinations
        '''
        assert isinstance(agency_tag, basestring), 'agency tag must be string type'
        assert isinstance(stop_id, basestring), 'stop id must be string type'
        assert destinations is None or isinstance(destinations, list)\
            or isinstance(destinations, basestring),\
            'include must be list, string, or null type'
        if agency_tag == 'bart':
            stop_title, route_tags = self.__validate_bart_station(stop_id,
                                                                  destinations)
            stop_tag = None
        else:
            stop_tag, stop_title, route_tags = \
                self.__validate_nextbus_stop(agency_tag,
                                             stop_id,
                                             destinations)
        # Add new leg object
        leg_data = {
            'stop_id' : stop_id.decode('utf-8'),
            'stop_title' : stop_title.decode('utf-8'),
            'agency' : agency_tag.decode('utf-8'),
        }
        if stop_tag:
            leg_data['stop_tag'] = stop_tag.decode('utf-8')
        else:
            leg_data['stop_tag'] = None
        new_leg = Leg(**leg_data)
        self.db_session.add(new_leg)
        self.db_session.commit()

        # Add all routes in leg includes
        route_tags = route_tags or []
        for tag in route_tags:
            leg_include = LegDestination(leg_id=new_leg.id,
                                         tag=tag.decode('utf-8'))
            self.db_session.add(leg_include)
        self.db_session.commit()

        # refresh here for better return
        new_leg = self.db_session.query(Leg).get(new_leg.id)
        leg = clean_sql(new_leg)
        leg['includes'] = route_tags
        return leg

    def leg_list(self):
        '''List all legs'''
        all_legs = self.db_session.query(Leg, LegDestination).join(LegDestination).all()
        leg_data = []
        last_leg = None
        for leg, leg_include in all_legs:
            tag = leg_include.tag.encode('utf-8')
            if last_leg is None or last_leg['id'] != leg.id: #pylint:disable=unsubscriptable-object
                clean_leg = clean_sql(leg)
                clean_leg['includes'] = [tag]
                leg_data.append(clean_leg)
                last_leg = clean_leg
                continue
            else:
                last_leg['includes'].append(tag)
        return leg_data

    def leg_delete(self, leg_id):
        '''Delete leg with given id
           leg_id : leg id
        '''
        assert isinstance(leg_id, int), 'leg id must be int type'
        trip_legs = self.db_session.query(TripLeg).\
            filter(TripLeg.leg_id == leg_id)
        for leg in trip_legs:
            raise TripPlannerException('Cannot delete leg, '
                                       'being used by a Trip:%s' % leg.trip_id)
        self.db_session.query(LegDestination).\
            filter(LegDestination.leg_id == leg_id).delete()
        self.db_session.commit()

        leg = self.db_session.query(Leg).get(leg_id)
        if not leg:
            raise TripPlannerException("no leg found with id:%s" % leg_id)
        self.db_session.delete(leg)
        self.db_session.commit()
        return True

    def leg_show(self, leg_id):
        '''Get predictions for leg with given id
           leg_id : leg id
        '''
        assert isinstance(leg_id, int), 'leg id must be int type'
        leg_query = self.db_session.query(Leg, LegDestination).join(LegDestination)
        leg_query = leg_query.filter(Leg.id == leg_id)
        if not leg_query:
            raise TripPlannerException("No Leg with this ID:%s" % leg_id)
        leggy = None
        includes = []
        for leg, leg_include in leg_query:
            if not leggy:
                leggy = clean_sql(leg)
            includes.append(leg_include.tag.encode('utf-8'))
        preds = None
        if leggy['agency'] == 'bart':
            preds = bart_client.station_departures(leggy['stop_id'],
                                                   destinations=includes)
        else:
            preds = nextbus_client.stop_prediction(leggy['agency'],
                                                   leggy['stop_id'],
                                                   route_tags=includes)
        return leggy['agency'], preds

    def trip_create(self, name, legs):
        '''Create a new trip with one or more legs
           name: name of new trip
           legs: one or more legs for trip to use
        '''
        assert isinstance(name, basestring), 'name must be string type'
        assert isinstance(legs, int) or isinstance(legs, list), 'legs must be list or int type'
        trip_data = {
            'name' : name.decode('utf-8')
        }
        new_trip = Trip(**trip_data)
        self.db_session.add(new_trip)
        self.db_session.commit()

        if isinstance(legs, int):
            legs = [legs]

        for leg in legs:
            new_leg = TripLeg(trip_id=new_trip.id,
                              leg_id=leg)
            self.db_session.add(new_leg)
        self.db_session.commit()

        new_trip = self.db_session.query(Trip).get(new_trip.id)
        return clean_sql(new_trip)

    def trip_list(self):
        '''List all trips'''
        trip_data = []
        all_trips = self.db_session.query(Trip, TripLeg).join(TripLeg).all()
        last_trip = None
        for trip, trip_leg in all_trips:
            if last_trip is None or last_trip['id'] != trip.id: #pylint:disable=unsubscriptable-object
                clean_trip = clean_sql(trip)
                clean_trip['legs'] = [trip_leg.leg_id]
                trip_data.append(clean_trip)
                last_trip = clean_trip
            else:
                last_trip['legs'].append(trip_leg.leg_id)
        return trip_data

    def trip_show(self, trip_id):
        '''Show all legs for a trip with given id
           trip_id: trip id
        '''
        assert isinstance(trip_id, int), 'trip id must be int type'
        try:
            self.db_session.query(Trip).get(trip_id)
        except UnmappedInstanceError:
            raise TripPlannerException("No Trip with ID:%s" % trip_id)
        nextbus_data = {}
        station_data = {}


        trip_query = self.db_session.query(TripLeg, Leg, LegDestination)
        trip_query = trip_query.join(Leg).join(LegDestination)
        trip_query = trip_query.filter(TripLeg.trip_id == trip_id)
        trip_query = trip_query.filter(TripLeg.leg_id == Leg.id)
        trip_query = trip_query.filter(LegDestination.leg_id == Leg.id)
        for _, leg, leg_include in trip_query:
            agency = leg.agency.encode('utf-8')
            stop_id = leg.stop_id.encode('utf-8')
            include_tag = leg_include.tag.encode('utf-8')
            if agency == 'bart':
                station_data.setdefault(stop_id, [])
                station_data[stop_id].append(include_tag)
            else:
                stop_tag = leg.stop_tag.encode('utf-8')
                nextbus_data.setdefault(agency, {})
                nextbus_data[agency].setdefault(stop_tag, [])
                nextbus_data[agency][stop_tag].append(include_tag)
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
        '''Delete trip with given id
           trip_id : trip id
        '''
        assert isinstance(trip_id, int), 'trip id must be int type'
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
