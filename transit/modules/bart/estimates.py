from transit.common import utils
from transit.urls import bart

class Estimate(object):
    def __init__(self, estimate_data, encoding):
        try:
            self.minutes = utils.pretty_strip(estimate_data.find('minutes'),
                                              encoding)
        except ValueError:
            # Most likely "Leaving"
            self.minutes = 0
        additional_keys = ['platform', 'direction', 'length', 'color']
        for key in additional_keys:
            setattr(self, key, utils.pretty_strip(estimate_data.find(key),
                                                  encoding))
        # True/False but given as 1/0
        self.bike_flag = int(utils.pretty_strip(estimate_data.find('bikeflag'),
                                                encoding)) == 1

    def __repr__(self):
        return '%s minutes' % self.minutes

class DirectionEstimates(object):
    def __init__(self, station_data, encoding):
        self.destination_name = utils.pretty_strip(station_data.find('destination'),
                                                   encoding)
        self.destination_abbreviation = utils.pretty_strip(station_data.find('abbreviation'),
                                                           encoding)
        self.estimates = \
            [Estimate(i, encoding) for i in station_data.find_all('estimate')]

    def __repr__(self):
        return '%s - %s' % (self.destination_name, self.estimates)

class StationDepartures(object):
    def __init__(self, station_data, encoding):
        self.station_name = utils.pretty_strip(station_data.find('name'),
                                               encoding)
        self.station_abbreviation = utils.pretty_strip(station_data.find('abbr'),
                                                       encoding)
        self.directions = \
            [DirectionEstimates(i, encoding) for i in station_data.find_all('etd')]

    def __repr__(self):
        return '%s - %s' % (self.station_name, self.directions)

def estimated_departures(station, platform=None, direction=None):
    url = bart.estimated_departures(station, platform=platform,
                                    direction=direction)
    soup, encoding = utils.make_request(url)
    return [StationDepartures(i, encoding) for i in soup.find_all('station')]
