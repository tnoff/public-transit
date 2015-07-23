main_url = "http://webservices.nextbus.com/service/publicXMLFeed"

def agency_list():
    return main_url + '?command=agencyList'

def route_list(agency_tag):
    return main_url + '?command=routeList&a=%s' % agency_tag

def route_show(agency_tag, route_tag):
    return main_url + '?command=routeConfig&a=%s&r=%s' % \
        (agency_tag, route_tag)

def stop_prediction(agency_tag, stop_id, route_tags=None):
    url = main_url + '?command=predictions&a=%s&stopId=%s' % \
        (agency_tag, stop_id)
    # if given one route, modify url to call it directly
    # if given more than one, do not add anything and let client handle
    # .. all roues
    if route_tags:
        if isinstance(route_tags, list):
            if len(route_tags) == 1:
                url += '&routeTag=%s' % route_tags[0]
        else:
            url += '&routeTag=%s' % route_tags
    return url

def multiple_stop_prediction(agency_tag, stop_data):
    # stop data: {route_tag : [stop_id, stop_id, ..], ...}
    url = main_url + '?command=predictionsForMultiStops&a=%s' % \
        (agency_tag)
    for route in stop_data:
        for stop in stop_data[route]:
            url += '&stops=%s|%s' % (route, stop)
    return url

def schedule_get(agency_tag, route_tag):
    return main_url + '?command=schedule&a=%s&r=%s' % \
        (agency_tag, route_tag)

def vehicle_location(agency_tag, route_tag, epoch_time):
    return main_url + '?command=vehicleLocations&a=%s&r=%s&t=%s' % \
        (agency_tag, route_tag, epoch_time)

def message_get(agency_tag, route_tags):
    if not isinstance(route_tags, list):
        route_tags = [route_tags]

    url = main_url + '?command=messages&a=%s' % agency_tag
    for tag in route_tags:
        url += '&r=%s' % tag
    return url
