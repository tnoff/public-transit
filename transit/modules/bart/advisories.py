from datetime import datetime

from transit.modules.bart import urls, utils

class ServiceAdvisory(object):
    def __init__(self, bsa_data, encoding):
        try:
            self.id = int(bsa_data.get('id').encode(encoding))
        except AttributeError:
            self.id = None
        try:
            self.station = utils.pretty_strip(bsa_data.find('station'),
                                              encoding)
        except (IndexError, AttributeError):
            self.station = None
        try:
            self.type = utils.pretty_strip(bsa_data.find('type'), encoding)
        except (IndexError, AttributeError):
            self.type = None
        self.description = utils.pretty_strip(bsa_data.find('description'),
                                              encoding)
        try:
            posted = utils.pretty_strip(bsa_data.find('posted'), encoding)
            self.posted = datetime.strptime(posted, '%a %b %d %Y %I:%M %p %Z')
        except (IndexError, AttributeError):
            self.posted = None
        try:
            expires = utils.pretty_strip(bsa_data.find('expires'), encoding)
            expires = bsa_data.find('expires').string.encode(encoding)
            self.expires = datetime.strptime(expires, '%a %b %d %Y %I:%M %p %Z')
        except (IndexError, AttributeError):
            self.expires = None

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
