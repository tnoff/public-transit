MAIN_URL = 'https://api.bart.gov/api/'

# service urls
def service_advisory(bart_api_key: str, date: str = 'today') -> str:
    return f'{MAIN_URL}bsa.aspx?cmd=bsa&key={bart_api_key}&date={date}&json=y'

def train_count(bart_api_key: str) -> str:
    return f'{MAIN_URL}bsa.aspx?cmd=count&key={bart_api_key}&json=y'

def elevator_status(bart_api_key: str) -> str:
    return f'{MAIN_URL}bsa.aspx?cmd=elev&key={bart_api_key}&json=y'

def station_list(bart_api_key: str) -> str:
    return f'{MAIN_URL}stn.aspx?cmd=stns&key={bart_api_key}&json=y'

def station_departures(bart_api_key: str, origin: str, platform: str | None = None, direction: str | None = None) -> str:
    url = f'{MAIN_URL}etd.aspx?cmd=etd&orig={origin}&key={bart_api_key}'
    if platform:
        url = f'{url}&plat={platform}'
    if direction:
        url = f'{url}&dir={direction}'
    return f'{url}&json=y'
