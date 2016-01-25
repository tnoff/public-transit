MAIN_URL = "http://webservices.nextbus.com/service/publicXMLFeed"

def agency_list():
    return MAIN_URL + '?command=agencyList'

def route_list(agency_tag):
    print agency_tag
    tag = agency_tag.lower()
    return MAIN_URL + '?command=routeList&a=%s' % tag

def route_show(agency_tag, route_tag):
    agency_tag = agency_tag.lower()
    route_tag = route_tag.lower()
    return MAIN_URL + '?command=routeConfig&a=%s&r=%s' % (agency_tag, route_tag)

def stop_prediction(agency_tag, stop_id, route_tags=None):
    agency_tag = agency_tag.lower()
    url = MAIN_URL + '?command=predictions&a=%s&stopId=%s' % (agency_tag, stop_id)
    if route_tags and not isinstance(route_tags, list):
        url += '&routeTag=%s' % route_tags.lower()
    return url

def multiple_stop_prediction(agency_tag, stop_data):
    # stop data: {stop_tag: [route_tag, route_tag, ..], ...}
    agency_tag = agency_tag.lower()
    url = MAIN_URL + '?command=predictionsForMultiStops&a=%s' % \
        (agency_tag)
    for stop_tag, routes in stop_data.items():
        for route in routes:
            routey = route.lower()
            url += '&stops=%s|%s' % (routey, stop_tag)
    return url

def schedule_get(agency_tag, route_tag):
    agency_tag = agency_tag.lower()
    route_tag = route_tag.lower()
    return MAIN_URL + '?command=schedule&a=%s&r=%s' % \
        (agency_tag, route_tag.lower())

def vehicle_location(agency_tag, route_tag, epoch_time):
    agency_tag = agency_tag.lower()
    route_tag = route_tag.lower()
    return MAIN_URL + '?command=vehicleLocations&a=%s&r=%s&t=%s' % \
        (agency_tag, route_tag.lower(), epoch_time)

def message_get(agency_tag, route_tags):
    agency_tag = agency_tag.lower()
    url = MAIN_URL + '?command=messages&a=%s' % agency_tag
    if not isinstance(route_tags, list):
        route_tags = [route_tags]
    for tag in route_tags:
        url += '&r=%s' % tag.lower()
    return url
