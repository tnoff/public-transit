from urllib.parse import quote

# 511.org SF Bay Area regional feed — one API over ~30 operators
# (SIRI). Common operator ids: SC=Santa Clara VTA, SF=SF Muni,
# CT=Caltrain, AC=AC Transit, GG=Golden Gate, SM=SamTrans, BA=BART.
BASE_URL = 'https://api.511.org/transit'

def operators(api_key: str) -> str:
    return f'{BASE_URL}/operators?api_key={quote(api_key)}&format=json'

def lines(api_key: str, operator: str) -> str:
    return f'{BASE_URL}/lines?api_key={quote(api_key)}&operator_id={quote(operator)}&format=json'

def stops(api_key: str, operator: str, line_id: str | None = None) -> str:
    url = f'{BASE_URL}/stops?api_key={quote(api_key)}&operator_id={quote(operator)}&format=json'
    if line_id:
        url = f'{url}&line_id={quote(str(line_id))}'
    return url

def stop_monitoring(api_key: str, operator: str, stop_code: str | None = None) -> str:
    url = f'{BASE_URL}/StopMonitoring?api_key={quote(api_key)}'\
          f'&agency={quote(operator)}&format=json'
    if stop_code:
        url = f'{url}&stopcode={quote(str(stop_code))}'
    return url
