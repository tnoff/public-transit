from urllib.parse import quote

MAIN_URL = "https://retro.umoiq.com/service/publicXMLFeed"

def agency_list() -> str:
    return f'{MAIN_URL}?command=agencyList'

def route_list(agency_tag: str) -> str:
    return f'{MAIN_URL}?command=routeList&a={quote(agency_tag)}'

def route_show(agency_tag: str, route_tag: str) -> str:
    return f'{MAIN_URL}?command=routeConfig&a={quote(agency_tag)}&r={quote(route_tag)}'

def stop_prediction(agency_tag: str, stop_id: str | int, route_tags: list[str] | str | None = None) -> str:
    url = f'{MAIN_URL}?command=predictions&a={quote(agency_tag)}&stopId={quote(str(stop_id))}'
    if route_tags and not isinstance(route_tags, list):
        url = f'{url}&routeTag={quote(str(route_tags))}'
    return url

def multiple_stop_prediction(agency_tag: str, stop_data: dict[str, list[str]]) -> str:
    # stop data: {stop_tag: [route_tag, route_tag, ..], ...}
    url = f'{MAIN_URL}?command=predictionsForMultiStops&a={quote(agency_tag)}'
    for stop_tag, routes in stop_data.items():
        for route in routes:
            url = f'{url}&stops={quote(str(route))}|{quote(str(stop_tag))}'
    return url

def message_get(agency_tag: str, route_tags: list[str] | str) -> str:
    url = f'{MAIN_URL}?command=messages&a={quote(agency_tag)}'
    if not isinstance(route_tags, list):
        route_tags = [route_tags]
    for tag in route_tags:
        url = f'{url}&r={quote(str(tag))}'
    return url
