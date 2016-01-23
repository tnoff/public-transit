from datetime import datetime

from transit.common import utils as common_utils
from transit.modules.nextbus import urls, utils

datetime_format = '%H:%M:%S'

def _schedule_route(schedule_data, encoding):
    data = {}
    tag = common_utils.parse_data(schedule_data, 'tag')
    data['tag'] = common_utils.clean_value(tag, encoding)
    title = common_utils.parse_data(schedule_data, 'title')
    data['title'] = common_utils.clean_value(title, encoding)
    schedule_class = common_utils.parse_data(schedule_data, 'scheduleclass')
    data['schedule_class'] = common_utils.clean_value(schedule_class, encoding)
    service_class = common_utils.parse_data(schedule_data, 'serviceclass')
    data['service_class'] = common_utils.clean_value(service_class, encoding)
    direction = common_utils.parse_data(schedule_data, 'direction')
    data['direction'] = common_utils.clean_value(direction, encoding)
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
    data = {}
    block_id = common_utils.parse_data(block_data, 'blockid')
    data['block_id'] = common_utils.clean_value(block_id, encoding)
    data['stop_schedules'] = []
    for new_stop in block_data.find_all('stop'):
        ss = _stop_schedule(new_stop, encoding)
        ss['title'] = title_data[ss['stop_tag']]
        data['stop_schedules'].append(ss)
    return data

def _stop_schedule(stop_data, encoding):
    data = {}
    stop_tag = common_utils.parse_data(stop_data, 'tag')
    data['stop_tag'] = common_utils.clean_value(stop_tag, encoding)
    epoch_time = common_utils.parse_data(stop_data, 'epochtime')
    data['epoch_time'] = common_utils.clean_value(epoch_time, encoding)
    # TODO figure out why clean value isnt working here
    time = common_utils.clean_value(stop_data.contents[0], encoding)
    if time == '--':
        data['time'] = None
    else:
        data['time'] = datetime.strptime(time, datetime_format)
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
