from transit.common import utils as common_utils
from transit.modules.nextbus import urls, utils

def _agency(agency_data, encoding):
    args = ['tag', 'title', 'regiontitle']
    data = common_utils.parse_page(agency_data, args, encoding)
    data['region'] = data.pop('regiontitle', None)
    return data

def agency_list():
    '''List all nextbus agencies'''
    url = urls.agency_list()
    soup, encoding = utils.make_request(url)
    return [_agency(ag, encoding) for ag in soup.find_all('agency')]
