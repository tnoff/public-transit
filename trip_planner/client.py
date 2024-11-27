from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.sql import text

from transit.modules.actransit import client as actransit
from transit.modules.bart import client as bart
from transit.modules.nextbus import client as nextbus
from transit.exceptions import TransitException

from trip_planner.tables import Base, Leg, LegDestination, Trip, TripLeg
from trip_planner.exceptions import TripPlannerException

def validate_bart_station(station_name, bart_api_key):
    '''
    Validate bart station with destinations
    '''
    # first check station is valid from list
    valid_stations = bart.station_list(bart_api_key)['stations']['station']
    for station in valid_stations:
        if station_name.lower() == station['abbr'].lower():
            return station_name.lower(), station['name']
    raise TripPlannerException(f'Bart station not valid: {station_name}')

def validate_nextbus_stop(agency_tag, stop_id):
    '''
    Validate nextbus stop with route tags (destinations)
    '''
    try:
        predictions = nextbus.stop_prediction(agency_tag, stop_id)['predictions']
    except TransitException as e:
        raise TripPlannerException(f'Could not identify stop: {str(e)}') from e

    stop_tag = None
    stop_title = None
    possible_routes = []
    for stop_pred in predictions:
        possible_routes.append(stop_pred['routeTag'])
        if not stop_tag:
            stop_tag = stop_pred['stopTag']
            stop_pred = stop_pred['stopTitle']
    return stop_tag, stop_title, possible_routes

def validate_actransit_stop(stop_id, actransit_api_key):
    '''
    Validate actransit stop with route tags
    '''
    stop_preds = actransit.stop_predictions(actransit_api_key, stop_id)
    return stop_preds['bustime-response']['prd'][0]['stpnm']

class TripPlanner():
    def __init__(self, database_path, bart_api_key=None, actransit_api_key=None):
        '''
        Trip planner client
        database_path   :   Path to sqlite database
        '''
        database_engine = create_engine(f'sqlite:///{database_path}')
        Base.metadata.create_all(database_engine)
        Base.metadata.bind = database_engine
        self.db_session = sessionmaker(bind=database_engine)()

        self.bart_api_key = bart_api_key
        self.actransit_api_key = actransit_api_key

    def leg_create(self, agency_tag, stop_id, destinations=None):
        '''
        Create a new leg with a given stop id and routes/destinations
        agency_tag          :   Agency tag
        stop_id             :   Identifier of stop
        destinations        :   Include only destinations
        '''
        # Stop tag used in nextbus api only
        stop_tag = None
        possible_routes = None
        # validate given stop
        if agency_tag == 'bart':
            stop_id, stop_title = validate_bart_station(stop_id, self.bart_api_key)
        elif agency_tag == 'actransit':
            stop_title = validate_actransit_stop(stop_id,
                                                 self.actransit_api_key)
        else:
            stop_tag, stop_title, possible_routes = validate_nextbus_stop(agency_tag, stop_id)

        # Add new leg object
        leg_data = {
            'stop_id' : stop_id,
            'stop_title' : stop_title,
            'agency' : agency_tag,
            'stop_tag': stop_tag,
        }
        new_leg = Leg(**leg_data)
        self.db_session.add(new_leg)
        self.db_session.commit()

        # Add all routes in leg includes
        destinations = destinations or []
        if agency_tag not in ['bart', 'actransit'] and not destinations:
            destinations = possible_routes
        for tag in destinations:
            leg_include = LegDestination(leg_id=new_leg.id, tag=tag)
            self.db_session.add(leg_include)
        self.db_session.commit()

        # refresh here for better return
        self.db_session.refresh(new_leg)
        leg_data['includes'] = sorted(destinations)
        return leg_data

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

    def leg_show(self, leg_id):
        '''
        Get predictions for leg with given id
        leg_id              :   Leg integer id
        '''
        leg = self.db_session.query(Leg).get(leg_id)
        if not leg:
            raise TripPlannerException(f'No Leg with this ID: {leg_id}')
        leg_query = self.db_session.query(Leg, LegDestination).\
                        join(LegDestination).filter(Leg.id == leg_id)
        includes = []
        for _leg, leg_include in leg_query:
            includes.append(leg_include.tag.lower())
        if leg.agency.lower() == 'bart':
            all_departures = bart.station_departures(self.bart_api_key, leg.stop_id)
            if not includes:
                return 'bart', all_departures['station']
            relevant_departures = []
            for station in all_departures['station']:
                for departure in station['etd']:
                    if departure['abbreviation'].lower() in includes:
                        relevant_departures.append(departure)
            return 'bart', relevant_departures

        if leg.agency.lower() == 'actransit':
            all_departures = actransit.stop_predictions(self.actransit_api_key,
                                                        leg.stop_id,
                                                        route_names=includes)['bustime-response']['prd']
            if not includes:
                return 'actransit', all_departures
            relevant_departures = []
            for departure in all_departures:
                if departure['rt'].lower() in includes:
                    relevant_departures.append(departure)
            return 'actransit', relevant_departures
        return leg.agency, nextbus.stop_prediction(leg.agency,
                                                   leg.stop_id,
                                                   route_tags=includes)['predictions']

    def leg_delete(self, leg_id):
        '''
        Delete leg with given id
        leg_id      :   leg integer id
        '''
        any_trip = self.db_session.query(TripLeg).filter(TripLeg.leg_id == leg_id).first()
        if any_trip:
            raise TripPlannerException(f'Trips currently using {leg_id}, cannot delete')
        self.db_session.query(LegDestination).filter(LegDestination.leg_id == leg_id).delete()
        self.db_session.query(Leg).filter(Leg.id == leg_id).delete()
        self.db_session.commit()
        self.db_session.execute(text("VACUUM"))
        return True

    def trip_create(self, name, legs): #pylint:disable=unused-argument
        '''
        Create a new trip with one or more legs
        name        :   name of new trip
        legs        :   one or more legs for trip to use
        '''
        new_trip = Trip(name=name)
        self.db_session.add(new_trip)
        self.db_session.commit()

        for leg_id in legs:
            leg = self.db_session.query(Leg).get(leg_id)
            if not leg:
                raise TripPlannerException(f'Leg does not exist {leg_id}')
            new_leg = TripLeg(trip_id=new_trip.id, leg_id=leg.id)
            self.db_session.add(new_leg)
        self.db_session.commit()

        new_trip = {
            'name': name,
            'legs': legs,
        }
        return new_trip

    def trip_list(self, **kwargs): #pylint:disable=unused-argument
        '''
        List all trips
        '''
        all_trips = []
        last_trip_id = None
        trip_data = None
        for trip, leg in self.db_session.query(Trip, TripLeg).\
                            filter(TripLeg.trip_id == Trip.id).all():
            if trip.id != last_trip_id:
                if trip_data is not None:
                    all_trips.append(trip_data)
                trip_data = trip.as_dict()
                trip_data['legs'] = []
                last_trip_id = trip.id
            trip_data['legs'].append(leg.id)
        all_trips.append(trip_data)
        return all_trips


    def trip_show(self, trip_id): #pylint:disable=too-many-locals,too-many-branches
        '''
        Show all legs for a trip with given id
        trip_id             :   Trip id
        '''
        try:
            self.db_session.query(Trip).get(trip_id)
        except UnmappedInstanceError as e:
            raise TripPlannerException(f'No Trip with ID: {trip_id}') from e

        trip_query = self.db_session.query(TripLeg, Leg).\
            filter(TripLeg.trip_id == trip_id).\
            filter(Leg.id == TripLeg.leg_id)

        # {bart_stop: [destination1, destination2]}
        bart_station_data = {}
        # {stop_id: [destination1, destination2]}
        actransit_data = {}
        # {stop_tag: [destination1, destination2]}
        nextbus_data = {}

        now = datetime.now()

        for _, leg in trip_query:
            if leg.agency == 'bart':
                bart_station_data.setdefault(leg.stop_id, set([]))
            elif leg.agency == 'actransit':
                actransit_data.setdefault(leg.stop_id, set([]))
            else:
                nextbus_data.setdefault(leg.agency, {})
                nextbus_data[leg.agency].setdefault(leg.stop_tag, set([]))

            for destination in self.db_session.query(LegDestination).\
                filter(LegDestination.leg_id == leg.id):
                if leg.agency == 'bart':
                    bart_station_data[leg.stop_id].add(destination.tag)
                    continue
                if leg.agency == 'actransit':
                    actransit_data[leg.stop_id].add(destination.tag)
                    continue
                nextbus_data[leg.agency][leg.stop_tag].add(destination.tag)

        trip_data = {
            'bart': {},
            'actransit': {},
            'nextbus': {},
        }
        if bart_station_data:
            for station in bart.station_departures(self.bart_api_key, 'all')['station']:
                if station['abbr'].lower() in bart_station_data:
                    destinations = bart_station_data[station['abbr'].lower()]
                    for dest in station['etd']:
                        if destinations and dest['abbreviation'].lower() not in destinations:
                            continue
                        trip_data['bart'].setdefault(station['name'], {})
                        trip_data['bart'][station['name']].setdefault(dest['destination'], [])
                        for estimate in dest['estimate']:
                            trip_data['bart'][station['name']][dest['destination']].\
                                append(int(estimate['minutes']) * 60)
        if actransit_data:
            for stop_id, destinations in actransit_data.items():
                for departure in actransit.stop_predictions(self.actransit_api_key,
                                                            stop_id,
                                                            route_names=destinations)['bustime-response']['prd']:
                    trip_data['actransit'].setdefault(departure['stpnm'], {})
                    trip_data['actransit'][departure['stpnm']].setdefault(departure['rt'], [])
                    est_datetime = datetime.strptime(departure['prdtm'], '%Y%m%d %H:%M')
                    est_seconds = (est_datetime - now).seconds
                    trip_data['actransit'][departure['stpnm']][departure['rt']].append(est_seconds)
        if nextbus_data:
            for agency, data in nextbus_data.items():
                trip_data.setdefault(agency, {})
                for pred in nextbus.stop_multiple_predictions(agency, data)['predictions']:
                    print(pred)
                    trip_data[agency].setdefault(pred['stopTitle'], {})
                    trip_data[agency][pred['stopTitle']].setdefault(pred['direction']['title'], [])
                    est_datetime = datetime.fromtimestamp(int(pred['direction']['prediction']['epochTime']) / 1000)
                    est_seconds = (est_datetime - now).seconds
                    trip_data[agency][pred['stopTitle']][pred['direction']['title']].append(est_seconds)
        return trip_data

    def trip_delete(self, trip_id):
        '''
        Delete trip with given id
        trip_id      :   trip integer id
        '''
        self.db_session.query(TripLeg).filter(TripLeg.trip_id == trip_id).delete()
        self.db_session.query(Trip).filter(Trip.id == trip_id).delete()
        self.db_session.commit()
        self.db_session.execute(text("VACUUM"))
        return True
