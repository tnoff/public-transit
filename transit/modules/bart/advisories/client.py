from datetime import datetime

from transit.urls import bart
from transit.common import utils

class ServiceAdvisory(object):
    def __init__(self, bsa_data):
        try:
            self.id = bsa_data.get('id').encode('iso-8859-1')
        except AttributeError:
            self.id = None
        try:
            self.station = bsa_data.find('station').contents[0].encode('iso-8859-1')
        except (IndexError, AttributeError):
            self.station = None
        try:
            self.type = bsa_data.find('type').contents[0].encode('iso-8859-1')
        except (IndexError, AttributeError):
            self.type = None
        descriptions = []
        for i in bsa_data.find('description').contents:
            s = i.encode('iso-8859-1')
            if s != '\n':
                descriptions.append(s)
        self.descriptions = descriptions
        try:
            posted = bsa_data.find('posted').contents[0].encode('iso-8859-1')
            self.posted = datetime.strptime(posted, '%a %b %d %Y %I:%M %p %Z')
        except (IndexError, AttributeError):
            self.posted = None
        try:
            expires = bsa_data.find('expires').contents[0].encode('iso-8859-1')
            self.expires = datetime.strptime(expires, '%a %b %d %Y %I:%M %p %Z')
        except (IndexError, AttributeError):
            self.expires = None

    def __repr__(self):
        return '%s - %s' % (self.station, self.descriptions)

def service_advisory():
    url = bart.service_advisory()
    soup = utils.make_request(url)
    return [ServiceAdvisory(bsa) for bsa in soup.find_all('bsa')]

def train_count():
    url = bart.train_count()
    soup = utils.make_request(url)
    return int(soup.find('traincount').contents[0].encode('iso-8859-1'))

def elevator_status():
    url = bart.elevator_status()
    soup = utils.make_request(url)
    return ServiceAdvisory(soup.find('bsa'))
