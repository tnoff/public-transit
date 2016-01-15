from datetime import datetime

from transit.common import utils as common_utils
from transit.modules.bart import urls, utils

datetime_format = '%a %b %d %Y %I:%M %p %Z'

def _service_advisory(bsa_data):
    data = {}
    args = ['id', 'station', 'type', 'description']
    for arg in args:
        value = common_utils.parse_data(bsa_data, arg)
        data[arg] = value
    args = ['posted', 'expires']
    for arg in args:
        value = common_utils.parse_data(bsa_data, arg)
        try:
            date_value = datetime.strptime(value, datetime_format)
        except TypeError:
            date_value = None
        data[arg] = date_value
    return data

def service_advisory():
    url = urls.service_advisory()
    soup, encoding = utils.make_request(url)
    return [_service_advisory(bsa) for bsa in soup.find_all('bsa')]

def train_count():
    url = urls.train_count()
    soup, encoding = utils.make_request(url)
    return int(soup.find('traincount').string.encode(encoding))

def elevator_status():
    url = urls.elevator_status()
    soup, encoding = utils.make_request(url)
    return _service_advisory(soup.find('bsa'))
