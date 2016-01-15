from datetime import datetime

from transit.common import utils as common_utils
from transit.modules.nextbus import urls, utils

def _schedule_route(schedule_data):
    data = {}
    data['tag'] = common_utils.parse_data(schedule_data, 'tag')
    data['title'] = common_utils.parse_data(schedule_data, 'title')
    data['schedule_class'] = common_utils.parse_data(schedule_data, 'scheduleclass')
    data['service_class'] = common_utils.parse_data(schedule_data, 'serviceclass')
    data['direction'] = common_utils.parse_data(schedule_data, 'direction')
    data['blocks'] = []

    # titles are put in the header for some reason
    # data: {tag: title, ...}
    title_data = dict()
    header = schedule_data.find('header')
    for new_stop in header.find_all('stop'):
        title_tag = common_utils.parse_data(new_stop, 'tag')
        title_data[title_tag] = new_stop.contents[0]
    # Then find all blocks and add them in
    data['blocks'] = [_schedule_block(i, title_data) for i in schedule_data.find_all('tr')]
    return data

def _schedule_block(block_data, title_data):
    data = {}
    data['block_id'] = common_utils.parse_data(block_data, 'blockid')
    data['stop_schedules'] = []
    for new_stop in block_data.find_all('stop'):
        ss = _stop_schedule(new_stop)
        ss['title'] = title_data[ss['stop_tag']]
        data['stop_schedules'].append(ss)
    return data

def _stop_schedule(stop_data, title=None):
    data = {}
    data['stop_tag'] = common_utils.parse_data(stop_data, 'tag')
    data['epoch_time'] = common_utils.parse_data(stop_data, 'epochtime')
    data['title'] = title
    time_data = stop_data.contents[0]
    if time_data == "--":
        data['time'] = None
    else:
        data['time'] = datetime.strptime(time_data, "%H:%M:%S")
    return data

def schedule_get(agency_tag, route_tag):
    url = urls.schedule_get(agency_tag, route_tag)
    soup, encoding = utils.make_request(url)
    return [_schedule_route(i) for i in soup.find_all('route')]
