from transit import utils

def agency(agency_data, encoding):
    args = ['tag', 'title', 'regiontitle']
    data = utils.parse_page(agency_data, args, encoding)
    data['region'] = data.pop('regiontitle', None)
    return data
