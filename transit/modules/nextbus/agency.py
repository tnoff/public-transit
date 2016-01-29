from transit.common import utils as common_utils

def agency(agency_data, encoding):
    args = ['tag', 'title', 'regiontitle']
    data = common_utils.parse_page(agency_data, args, encoding)
    data['region'] = data.pop('regiontitle', None)
    return data
