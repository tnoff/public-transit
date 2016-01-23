from transit.common import utils as common_utils
from transit.modules.nextbus import urls, utils

datetime_format = '%H:%M:%S'

def _schedule_route(schedule_data, encoding):
    args = ['tag', 'title', 'scheduleclass', 'serviceclass', 'direction']
    data = common_utils.parse_page(schedule_data, args, encoding)
    data['schedule_class'] = data.pop('scheduleclass', None)
    data['service_class'] = data.pop('serviceclass', None)
    data['blocks'] = []

    # titles are put in the header for some reason
    # data: {tag: title, ...}
    title_data = dict()
    header = schedule_data.find('header')
    for new_stop in header.find_all('stop'):
        title_tag = common_utils.parse_data(new_stop, 'tag')
        title_data[title_tag] = common_utils.clean_value(new_stop.contents[0], encoding)
    # Then find all blocks and add them in
    for tr in schedule_data.find_all('tr'):
        data['blocks'].append(_schedule_block(tr, encoding, title_data))
    return data

def _schedule_block(block_data, encoding, title_data):
    data = common_utils.parse_page(block_data, ['blockid'], encoding)
    data['block_id'] = data.pop('blockid', None)
    data['stop_schedules'] = []
    for new_stop in block_data.find_all('stop'):
        ss = _stop_schedule(new_stop, encoding)
        ss['title'] = title_data[ss['stop_tag']]
        data['stop_schedules'].append(ss)
    return data

def _stop_schedule(stop_data, encoding):
    args = ['tag', 'epochtime']
    data = common_utils.parse_page(stop_data, args, encoding)
    data['stop_tag'] = data.pop('tag', None)
    data['epoch_time'] = data.pop('epochtime', None)
    time_data = stop_data.contents[0]
    time = common_utils.clean_value(time_data, encoding,
                                    datetime_format=datetime_format)
    if time == '--':
        data['time'] = None
    return data

def schedule_get(agency_tag, route_tag):
    '''Get schedule information for route
       agency_tag : agency tag
       route_tag : route tag
    '''
    assert isinstance(agency_tag, basestring), 'agency tag must be string type'
    assert isinstance(route_tag, basestring), 'route tag must be string type'
    url = urls.schedule_get(agency_tag, route_tag)
    soup, encoding = utils.make_request(url)
    return [_schedule_route(route, encoding) for route in soup.find_all('route')]
