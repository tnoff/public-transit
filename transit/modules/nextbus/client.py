from transit.modules.nextbus import agency, route, stop, schedule, vehicle

def agency_list():
    return agency.list_all()

def route_list(agency_tag):
    return route.route_list(agency_tag)

def route_get(agency_tag, route_tag):
    return route.route_get(agency_tag, route_tag)

def stop_prediction(agency_tag, stop_id, route_tag=None):
    return stop.stop_prediction(agency_tag, stop_id, route_tag=route_tag)

def multiple_stop_predictions(agency_tag, stop_data):
    return stop.multiple_stop_prediction(agency_tag, stop_data)

def schedule_get(agency_tag, route_tag):
    return schedule.schedule_get(agency_tag, route_tag)

def vehicle_location(agency_tag, route_tag, epoch_time):
    return vehicle.vehicle_location(agency_tag, route_tag, epoch_time)

def message_get(agency_tag, route_tags):
    return route.message_get(agency_tag, route_tags)