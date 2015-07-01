from transit.common import utils
from transit.urls import bart

class Estimate(object):
    def __init__(self, estimate_data, encoding):
        try:
            self.minutes = estimate_data.find('minutes').string.encode(encoding)
        except ValueError:
            # Most likely "Leaving"
            self.minutes = 0
        self.platform = int(estimate_data.find('platform').string.encode(encoding))
        self.direction = estimate_data.find('direction').string.encode(encoding)
        self.length = estimate_data.find('length').string.encode(encoding)
        self.color = estimate_data.find('color').string.encode(encoding)
        # True/False but given as 1/0
        self.bike_flag = \
            int(estimate_data.find('bikeflag').string.encode(encoding)) == 1

    def __repr__(self):
        return '%s minutes' % self.minutes

class DirectionEstimates(object):
    def __init__(self, station_data, encoding):
        self.destination_name = \
            station_data.find('destination').string.encode(encoding)
        self.destination_abbreviation = \
            station_data.find('abbreviation').string.encode(encoding)
        self.estimates = \
            [Estimate(i, encoding) for i in station_data.find_all('estimate')]

    def __repr__(self):
        return '%s - %s' % (self.destination_name, self.estimates)

class StationDepartures(object):
    def __init__(self, station_data, encoding):
        self.station_name = station_data.find('name').string.encode(encoding)
        self.station_abbreviation = \
            station_data.find('abbr').string.encode(encoding)
        self.directions = \
            [DirectionEstimates(i, encoding) for i in station_data.find_all('etd')]

    def __repr__(self):
        return '%s - %s' % (self.station_name, self.directions)

def estimated_departures(station, platform=None, direction=None):
    url = bart.estimated_departures(station, platform=platform,
                                    direction=direction)
    soup, encoding = utils.make_request(url)
    return [StationDepartures(i, encoding) for i in soup.find_all('station')]
