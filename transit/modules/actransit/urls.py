BASE_URL = 'https://api.actransit.org/transit/'

def route_list(token: str) -> str:
    return f'{BASE_URL}/routes/?token={token}'

def route_directions(token: str, route_name: str) -> str:
    return f'{BASE_URL}/route/{route_name}/directions/?token={token}'

def route_trips(token: str, route_name: str, direction: str, schedule_type: int) -> str:
    return f'{BASE_URL}/route/{route_name}/trips?direction={direction}'\
           f'&scheduleType={schedule_type}&token={token}'

def route_stops(token: str, route_name: str, trip_id: str) -> str:
    return f'{BASE_URL}/route/{route_name}/trip/{trip_id}/stops/?token={token}'

def stop_predictions(token: str, stop_ids: list[str] | str, route_names: list[str] | None) -> str:
    if not isinstance(stop_ids, list):
        stop_ids = [stop_ids]
    stops = ','.join(f'{stop_id}' for stop_id in stop_ids)
    url = f'{BASE_URL}/actrealtime/prediction?stpid={stops}'
    if route_names:
        url = f'{url}&rt={",".join(route for route in route_names)}'
    return f'{url}&token={token}'

def service_notices(token: str) -> str:
    return f'{BASE_URL}/servicenotices/?token={token}'
