from datetime import datetime

from transit.common import utils as common_utils
from transit.modules.bart import urls, utils

datetime_format = '%a %b %d %Y %I:%M %p %Z'

class ServiceAdvisory(object):
    def __init__(self, bsa_data, encoding):
        self.id = common_utils.parse_data(bsa_data, 'id', encoding)
        self.station = common_utils.parse_data(bsa_data, 'station', encoding)
        self.type = common_utils.parse_data(bsa_data, 'type', encoding)
        self.description = common_utils.parse_data(bsa_data, 'description', encoding)

        self.posted = common_utils.parse_data(bsa_data, 'posted', encoding,
                                              datetime_format=datetime_format)
        self.expires = common_utils.parse_data(bsa_data, 'expires', encoding,
                                               datetime_format=datetime_format)

    def __repr__(self):
        return '%s - %s' % (self.station, self.description)

def service_advisory():
    url = urls.service_advisory()
    soup, encoding = utils.make_request(url)
    return [ServiceAdvisory(bsa, encoding) for bsa in soup.find_all('bsa')]

def train_count():
    url = urls.train_count()
    soup, encoding = utils.make_request(url)
    return int(soup.find('traincount').string.encode(encoding))

def elevator_status():
    url = urls.elevator_status()
    soup, encoding = utils.make_request(url)
    return ServiceAdvisory(soup.find('bsa'), encoding)
