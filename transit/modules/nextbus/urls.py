main_url = "http://webservices.nextbus.com/service/publicXMLFeed"

def agency_list():
    return main_url + '?command=agencyList'

def route_list(agency_tag):
    return main_url + '?command=routeList&a=%s' % agency_tag

def route_show(agency_tag, route_tag):
    if not isinstance(route_tag, str):
        route_tag = '%s' % route_tag
    return main_url + '?command=routeConfig&a=%s&r=%s' % \
        (agency_tag, route_tag.upper())

def stop_prediction(agency_tag, stop_id, route_tags=None):
    url = main_url + '?command=predictions&a=%s&stopId=%s' % \
        (agency_tag, stop_id)
    # if given one route, modify url to call it directly
    # if given more than one, do not add anything and let client handle
    # .. all roues
    if route_tags:
        if isinstance(route_tags, list):
            if len(route_tags) == 1:
                if not isinstance(route_tags[0], str):
                    route_tags[0] = '%s' % route_tags[0].upper()
                url += '&routeTag=%s' % route_tags[0].upper()
        else:
            if not isinstance(route_tags, str):
                route_tags = '%s' % route_tags.upper()
            url += '&routeTag=%s' % route_tags.upper()
    return url

def multiple_stop_prediction(agency_tag, stop_data):
    # stop data: {route_tag : [stop_id, stop_id, ..], ...}
    url = main_url + '?command=predictionsForMultiStops&a=%s' % \
        (agency_tag)
    for route in stop_data:
        if not isinstance(route, str):
            route = '%s' % route
        for stop in stop_data[route]:
            url += '&stops=%s|%s' % (route.upper(), stop)
    return url

def schedule_get(agency_tag, route_tag):
    if not isinstance(route_tag, str):
        route_tag = '%s' % route_tag
    return main_url + '?command=schedule&a=%s&r=%s' % \
        (agency_tag, route_tag.upper())

def vehicle_location(agency_tag, route_tag, epoch_time):
    if not isinstance(route_tag, str):
        route_tag = '%s' % route_tag
    return main_url + '?command=vehicleLocations&a=%s&r=%s&t=%s' % \
        (agency_tag, route_tag.upper(), epoch_time)

def message_get(agency_tag, route_tags):
    if not isinstance(route_tags, list):
        route_tags = [route_tags]

    url = main_url + '?command=messages&a=%s' % agency_tag
    for tag in route_tags:
        if not isinstance(tag, str):
            tag = '%s' % tag
        url += '&r=%s' % tag.upper()
    return url
