MAIN_URL = "http://webservices.nextbus.com/service/publicXMLFeed"

def agency_list():
    return '%s?command=agencyList' % MAIN_URL

def route_list(agency_tag):
    return '%s?command=routeList&a=%s' % (MAIN_URL, agency_tag)

def route_show(agency_tag, route_tag):
    return '%s?command=routeConfig&a=%s&r=%s' % (MAIN_URL, agency_tag, route_tag)

def stop_prediction(agency_tag, stop_id, route_tags=None):
    url = '%s?command=predictions&a=%s&stopId=%s' % (MAIN_URL, agency_tag, stop_id)
    if route_tags and not isinstance(route_tags, list):
        url = '%s&routeTag=%s' % (url, route_tags)
    return url

def multiple_stop_prediction(agency_tag, stop_data):
    # stop data: {stop_tag: [route_tag, route_tag, ..], ...}
    url = '%s?command=predictionsForMultiStops&a=%s' % (MAIN_URL, agency_tag)
    for stop_tag, routes in stop_data.items():
        for route in routes:
            url = '%s&stops=%s|%s' % (url, route, stop_tag)
    return url

def schedule_get(agency_tag, route_tag):
    return '%s?command=schedule&a=%s&r=%s' % (MAIN_URL, agency_tag, route_tag)

def vehicle_location(agency_tag, route_tag, epoch_time):
    return '%s?command=vehicleLocations&a=%s&r=%s&t=%s' % (MAIN_URL, agency_tag, route_tag, epoch_time)

def message_get(agency_tag, route_tags):
    url = '%s?command=messages&a=%s' % (MAIN_URL, agency_tag)
    if not isinstance(route_tags, list):
        route_tags = [route_tags]
    for tag in route_tags:
        url = '%s&r=%s' % (url, tag)
    return url
