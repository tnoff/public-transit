from transit.common import utils as common_utils
from transit.modules.bart import urls, utils

datetime_format = '%a %b %d %Y %I:%M %p %Z'

def _service_advisory(bsa_data, encoding):
    data = {}
    args = ['id', 'station', 'type', 'description', 'posted', 'expires']
    for arg in args:
        value = common_utils.parse_data(bsa_data, arg)
        data[arg] = common_utils.clean_value(value, encoding, datetime_format=datetime_format)
    return data

def service_advisory():
    url = urls.service_advisory()
    soup, encoding = utils.make_request(url)
    service_advisories = []
    for bsa in soup.find_all('bsa'):
        service_data = _service_advisory(bsa, encoding)
        service_advisories.append(service_data)
    return service_advisories

def train_count():
    url = urls.train_count()
    soup, encoding = utils.make_request(url)
    return int(soup.find('traincount').string.encode(encoding))

def elevator_status():
    url = urls.elevator_status()
    soup, encoding = utils.make_request(url)
    service_data = _service_advisory(soup.find('bsa'), encoding)
    return service_data
