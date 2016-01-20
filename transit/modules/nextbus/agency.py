from transit.common import utils as common_utils
from transit.modules.nextbus import urls, utils

def _agency(agency_data, encoding):
    data = {}
    args = ['tag', 'title', 'regiontitle']
    for arg in args:
        value = common_utils.parse_data(agency_data, arg)
        data[arg] = common_utils.clean_value(value, encoding)
    data['region'] = data.pop('regiontitle', None)
    return data

def list_all():
    url = urls.agency_list()
    soup, encoding = utils.make_request(url)
    return [_agency(ag, encoding) for ag in soup.find_all('agency')]
