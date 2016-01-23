from transit.common import utils as common_utils
from transit.modules.bart import urls, utils

datetime_format = '%a %b %d %Y %I:%M %p %Z'

def _service_advisory(bsa_data, encoding):
    args = ['id', 'station', 'type', 'description', 'posted', 'expires']
    return common_utils.parse_page(bsa_data, args, encoding,
                                   datetime_format=datetime_format)

def service_advisory():
    '''System wide service advisory'''
    url = urls.service_advisory()
    soup, encoding = utils.make_request(url)
    service_advisories = []
    for bsa in soup.find_all('bsa'):
        service_data = _service_advisory(bsa, encoding)
        service_advisories.append(service_data)
    return service_advisories

def train_count():
    '''System wide train count'''
    url = urls.train_count()
    soup, encoding = utils.make_request(url)
    return int(soup.find('traincount').string.encode(encoding))

def elevator_status():
    '''System wide elevator status'''
    url = urls.elevator_status()
    soup, encoding = utils.make_request(url)
    return _service_advisory(soup.find('bsa'), encoding)
