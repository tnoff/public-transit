from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import UnmappedInstanceError

from transit import bart
from transit.exceptions import TransitException
from transit import nextbus

from trip_planner.database.tables import Base, Leg, LegDestination, Trip, TripLeg
from trip_planner.exceptions import TripPlannerException

def validate_bart_station(stop_tag, destinations, verify_destinations=True, api_key=None):
    '''
    Validate bart station with destinations
    '''
    # first check station is valid from list
    valid_stations = bart.station_list()
    if stop_tag.lower() not in [i for i in valid_stations]:
        raise TripPlannerException('Bart station not valid:%s' % stop_tag)

    station_name = valid_stations[stop_tag]

    if verify_destinations:
        # check for all possible routes from station
        # use this to get a list of all possible destinations
        possible_destinations = set([])
        station = bart.station_info(stop_tag.lower(), api_key=api_key)
        north_routes = station['north_routes'] or []
        south_routes = station['south_routes'] or []
        all_routes = set(north_routes + south_routes)
        for route_number in sorted(all_routes):
            route = bart.route_info(route_number, api_key=api_key)
            possible_destinations.add(route['destination'].lower())

        # if destinations given, check given destinations against possible destinations
        # .. make sure all are valid
        if destinations:
            if not isinstance(destinations, list):
                destinations = [destinations]
            for destination in sorted(destinations):
                if destination not in possible_destinations:
                    raise TripPlannerException("Invalid destination:%s" % destination)
        elif not destinations:
            destinations = list(possible_destinations)
    return station_name, destinations

def validate_nextbus_stop(db_session, agency_tag, stop_id, route_tags, validate_route_tags=True):
    '''
    Validate nextbus stop with route tags (destinations)
    '''
    try:
        predictions = nextbus.stop_prediction(agency_tag,
                                              stop_id)
    except TransitException as e:
        raise TripPlannerException("Could not identify stop:%s" % str(e))

    # here is the best time to get a route tag for the stop
    # this is the only way to get a stop tag, which is different than
    # .. the stop id used here. this is an intentional design because
    # .. the call used for getting a single stop prediction uses stop id
    # .. while the prediction method for multiple stops at a time uses
    # .. the stop tag
    # using multiple stops is a good way of saving time by elimating
    # .. the need for multiple calls to the nextbus api

    # first get all possible routes
    possible_routes = [route['route_tag'] for route in predictions]
    # check if another leg is using the same agency and tag
    # if so, use that leg to get the stop tag
    leg = db_session.query(Leg).filter(Leg.stop_id == stop_id).\
            filter(Leg.agency == agency_tag).first()
    stop_tag = None
    stop_title = None
    stop_id = stop_id

    if leg is not None:
        stop_tag = leg.stop_tag
        stop_title = leg.stop_title
        stop_id = stop_id

    # if not, iterate through each route
    # .. for each route, go through every stop
    # .. check if stop id matches, if so use that same tag and exit
    else:
        found_route = False
        for route_tag in sorted(possible_routes):
            route = nextbus.route_show(agency_tag, route_tag)
            for stop in route['stops']:
                if stop['stop_id'] == stop_id:
                    stop_tag = stop['stop_tag']
                    stop_title = stop['title']
                    found_route = True
                    break
            if found_route:
                break

    if not validate_route_tags:
        return stop_tag, stop_title, route_tags

    # also return a list of all possible route_tags from predictions
    # .. this is also needed for the multiple stop logic later
    if route_tags is None:
        return stop_tag, stop_title, possible_routes

    if not isinstance(route_tags, list):
        route_tags = [route_tags]

    for route in route_tags:
        if route not in possible_routes:
            raise TripPlannerException("Invalid route given:%s" % route)
    return stop_tag, stop_title, route_tags

class TripPlanner():
    def __init__(self, database_path):
        '''
        Trip planner client
        database_path   :   Path to sqlite database
        '''
        database_engine = create_engine('sqlite:///%s' % database_path)
        Base.metadata.create_all(database_engine)
        Base.metadata.bind = database_engine
        self.db_session = sessionmaker(bind=database_engine)()

    def leg_create(self, agency_tag, stop_id, destinations=None, force=False, bart_api_key=None):
        '''
        Create a new leg with a given stop id and routes/destinations
        agency_tag      :   agency tag
        stop_id         :   identifier of stop
        include         :   include only destinations
        bart_api_key    : Use specific bart API key
        '''
        assert isinstance(agency_tag, str), 'agency tag must be string type'
        assert isinstance(stop_id, str), 'stop id must be string type'
        assert destinations is None or isinstance(destinations, (str, list)), \
            'include must be list, string, or null type'
        if isinstance(destinations, list):
            for destination in destinations:
                assert isinstance(destination, str), 'destination must be  string type'
        assert isinstance(force, bool), 'force must be boolean value'
        # validate given stop
        if agency_tag == 'bart':
            stop_title, route_tags = validate_bart_station(stop_id, destinations,
                                                           verify_destinations=not force,
                                                           api_key=bart_api_key)
            stop_tag = None
        else:
            stop_tag, stop_title, route_tags = validate_nextbus_stop(self.db_session,
                                                                     agency_tag,
                                                                     stop_id,
                                                                     destinations,
                                                                     validate_route_tags=not force)
        # Add new leg object
        leg_data = {
            'stop_id' : stop_id,
            'stop_title' : stop_title,
            'agency' : agency_tag,
        }
        if stop_tag:
            leg_data['stop_tag'] = stop_tag
        else:
            leg_data['stop_tag'] = None
        new_leg = Leg(**leg_data)
        self.db_session.add(new_leg)
        self.db_session.commit()

        # Add all routes in leg includes
        route_tags = route_tags or []
        for tag in route_tags:
            leg_include = LegDestination(leg_id=new_leg.id, tag=tag)
            self.db_session.add(leg_include)
        self.db_session.commit()

        # refresh here for better return
        self.db_session.refresh(new_leg)
        leg = new_leg.as_dict()
        leg['includes'] = sorted(route_tags)
        return leg

    def leg_list(self):
        '''
        List all legs, along with their given routes/destinations
        '''
        all_legs = []
        for leg in self.db_session.query(Leg).all():
            leg_data = leg.as_dict()
            leg_data['destinations'] = []
            for destination in self.db_session.query(LegDestination).\
                    filter(LegDestination.leg_id == leg.id):
                leg_data['destinations'].append(destination.tag)
            all_legs.append(leg_data)
        return all_legs

    def leg_delete(self, leg_id):
        '''
        Delete leg with given id
        leg_id      :   leg integer id(s)
        '''
        if not isinstance(leg_id, list):
            assert isinstance(leg_id, int), 'leg id must be int type'
            leg_id = [leg_id]
        deleted_ids = []
        for leg in leg_id:
            self.__leg_delete(leg)
            deleted_ids.append(leg)
        self.db_session.execute("VACUUM")
        return deleted_ids

    def __leg_delete(self, leg_id):
        trip_leg = self.db_session.query(TripLeg).filter(TripLeg.leg_id == leg_id).first()
        if trip_leg is not None:
            raise TripPlannerException('Cannot delete leg'\
                ', being used by a Trip:%s' % trip_leg.trip_id)
        self.db_session.query(LegDestination).\
            filter(LegDestination.leg_id == leg_id).delete()
        self.db_session.commit()

        leg = self.db_session.query(Leg).get(leg_id)
        if not leg:
            raise TripPlannerException("no leg found with id:%s" % leg_id)
        self.db_session.delete(leg)
        self.db_session.commit()
        return True

    def leg_show(self, leg_id, bart_api_key=None):
        '''
        Get predictions for leg with given id
        leg_id      :   leg integer id
        bart_api_key    : Use specific bart API key
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
                leggy = leg.as_dict()
            includes.append(leg_include.tag)
        if leggy['agency'] == 'bart':
            return 'bart', bart.station_departures(leggy['stop_id'],
                                                   destinations=includes, api_key=bart_api_key)
        return leggy['agency'], nextbus.stop_prediction(leggy['agency'],
                                                        leggy['stop_id'],
                                                        route_tags=includes)

    def trip_create(self, name, legs):
        '''
        Create a new trip with one or more legs
        name        :   name of new trip
        legs        :   one or more legs for trip to use
        '''
        assert isinstance(name, str), 'name must be string type'
        assert isinstance(legs, (list, int)), 'legs must be list or int type'
        if isinstance(legs, list):
            for leg in legs:
                assert isinstance(leg, int), 'leg must be int type'
        trip_data = {'name' : name}
        new_trip = Trip(**trip_data)
        self.db_session.add(new_trip)
        self.db_session.commit()

        if isinstance(legs, int):
            legs = [legs]

        for leg in legs:
            new_leg = TripLeg(trip_id=new_trip.id, leg_id=leg)
            self.db_session.add(new_leg)
        self.db_session.commit()

        self.db_session.refresh(new_trip)
        new_trip = new_trip.as_dict()
        new_trip['legs'] = legs
        return new_trip

    def trip_list(self):
        '''
        List all trips
        '''
        all_trips = []
        for trip in self.db_session.query(Trip).all():
            trip_data = trip.as_dict()
            trip_data['legs'] = []
            for leg in self.db_session.query(TripLeg).filter(TripLeg.trip_id == trip.id):
                trip_data['legs'].append(leg.leg_id)
            all_trips.append(trip_data)
        return all_trips

    def trip_show(self, trip_id, bart_api_key=None):
        '''
        Show all legs for a trip with given id
        trip_id     :   trip id
        bart_api_key    : Use specific bart API key
        '''
        assert isinstance(trip_id, int), 'trip id must be int type'
        try:
            self.db_session.query(Trip).get(trip_id)
        except UnmappedInstanceError:
            raise TripPlannerException("No Trip with ID:%s" % trip_id)

        trip_query = self.db_session.query(TripLeg, Leg, LegDestination)
        trip_query = trip_query.filter(TripLeg.trip_id == trip_id)
        trip_query = trip_query.filter(TripLeg.leg_id == Leg.id)
        trip_query = trip_query.filter(LegDestination.leg_id == Leg.id)

        nextbus_data = {}
        station_data = {}

        for _, leg, leg_include in trip_query:
            agency = leg.agency
            stop_id = leg.stop_id
            include_tag = leg_include.tag
            if agency == 'bart':
                station_data.setdefault(stop_id, [])
                station_data[stop_id].append(include_tag)
            else:
                nextbus_data.setdefault(agency, {})
                nextbus_data[agency].setdefault(leg.stop_tag, [])
                nextbus_data[agency][leg.stop_tag].append(include_tag)

        trip_data = dict()

        if station_data:
            trip_data['bart'] = bart.station_multiple_departures(station_data, api_key=bart_api_key)
        trip_data['nextbus'] = []
        for agency, data in nextbus_data.items():
            trip_data['nextbus'] += nextbus.stop_multiple_predictions(agency, data)
        return trip_data

    def trip_delete(self, trip_id):
        '''
        Delete trip with given id
        trip_id     :   trip id(s)
        '''
        if not isinstance(trip_id, list):
            assert isinstance(trip_id, int), 'trip id must be int type'
            trip_id = [trip_id]

        deleted_trips = []
        for trip in trip_id:
            self.__trip_delete(trip)
            deleted_trips.append(trip)
        self.db_session.execute("VACUUM")
        return deleted_trips

    def __trip_delete(self, trip_id):
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
