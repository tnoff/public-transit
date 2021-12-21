MAIN_URL = "https://retro.umoiq.com/service/publicXMLFeed"

def agency_list():
    return f'{MAIN_URL}?command=agencyList'

def route_list(agency_tag):
    return f'{MAIN_URL}?command=routeList&a={agency_tag}'

def route_show(agency_tag, route_tag):
    return f'{MAIN_URL}?command=routeConfig&a={agency_tag}&r={route_tag}'

def stop_prediction(agency_tag, stop_id, route_tags=None):
    url = f'{MAIN_URL}?command=predictions&a={agency_tag}&stopId={stop_id}'
    if route_tags and not isinstance(route_tags, list):
        url = f'{url}&routeTag={route_tags}'
    return url

def multiple_stop_prediction(agency_tag, stop_data):
    # stop data: {stop_tag: [route_tag, route_tag, ..], ...}
    url = f'{MAIN_URL}?command=predictionsForMultiStops&a={agency_tag}'
    for stop_tag, routes in stop_data.items():
        for route in routes:
            url = f'{url}&stops={route}|{stop_tag}'
    return url

def message_get(agency_tag, route_tags):
    url = f'{MAIN_URL}?command=messages&a={agency_tag}'
    if not isinstance(route_tags, list):
        route_tags = [route_tags]
    for tag in route_tags:
        url = f'{url}&r={tag}'
    return url
