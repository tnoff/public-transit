from datetime import datetime

from transit.urls import bart
from transit.common import utils

class ServiceAdvisory(object):
    def __init__(self, bsa_data, encoding):
        try:
            self.id = bsa_data.get('id').encode(encoding)
        except AttributeError:
            self.id = None
        try:
            self.station = bsa_data.find('station').string.encode(encoding)
        except (IndexError, AttributeError):
            self.station = None
        try:
            self.type = bsa_data.find('type').string.encode(encoding)
        except (IndexError, AttributeError):
            self.type = None
        descriptions = []
        for i in bsa_data.find('description').contents:
            s = i.encode(encoding)
            if s != '\n':
                descriptions.append(s)
        self.descriptions = descriptions
        try:
            posted = bsa_data.find('posted').string.encode(encoding)
            self.posted = datetime.strptime(posted, '%a %b %d %Y %I:%M %p %Z')
        except (IndexError, AttributeError):
            self.posted = None
        try:
            expires = bsa_data.find('expires').string.encode(encoding)
            self.expires = datetime.strptime(expires, '%a %b %d %Y %I:%M %p %Z')
        except (IndexError, AttributeError):
            self.expires = None

    def __repr__(self):
        return '%s - %s' % (self.station, self.descriptions)

def service_advisory():
    url = bart.service_advisory()
    soup, encoding = utils.make_request(url)
    return [ServiceAdvisory(bsa, encoding) for bsa in soup.find_all('bsa')]

def train_count():
    url = bart.train_count()
    soup, encoding = utils.make_request(url)
    return int(soup.find('traincount').string.encode(encoding))

def elevator_status():
    url = bart.elevator_status()
    soup, encoding = utils.make_request(url)
    return ServiceAdvisory(soup.find('bsa'), encoding)
