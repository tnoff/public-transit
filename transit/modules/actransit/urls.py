BASE_URL = 'https://api.actransit.org/transit/'

def route_list(token):
    return '%s/routes/?token=%s' % (BASE_URL, token)

def route_directions(token, route_name):
    return '%s/route/%s/directions/?token=%s' % (BASE_URL, route_name, token)

def route_trips(token, route_name, direction, schedule_type):
    return '%s/route/%s/trips?direction=%s&scheduleType=%s&token=%s' % \
        (BASE_URL, route_name, direction, schedule_type, token)

def route_stops(token, route_name, trip_id):
    return '%s/route/%s/trip/%s/stops/?token=%s' % \
        (BASE_URL, route_name, trip_id, token)

def stop_predictions(token, stop_ids, route_names):
    stops = ','.join('%s' % stop_id for stop_id in stop_ids)
    url = '%s/actrealtime/prediction?stpid=%s' % (BASE_URL, stops)
    if route_names:
        url = '%s&rt=%s' % (url, ','.join(route for route in route_names))
    return '%s&token=%s' % (url, token)

def service_notices(token):
    return '%s/servicenotices/?token=%s' % (BASE_URL, token)
