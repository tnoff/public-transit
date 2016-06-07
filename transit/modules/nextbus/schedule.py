from transit import utils

datetime_format = '%H:%M:%S'

def schedule_route(schedule_data, encoding):
    args = ['tag', 'title', 'scheduleclass', 'serviceclass', 'direction']
    data = utils.parse_page(schedule_data, args, encoding)
    data['schedule_class'] = data.pop('scheduleclass', None)
    data['service_class'] = data.pop('serviceclass', None)
    data['blocks'] = []

    # titles are put in the header for some reason
    # data: {tag: title, ...}
    title_data = dict()
    header = schedule_data.find('header')
    for new_stop in header.find_all('stop'):
        title_tag = utils.parse_data(new_stop, 'tag')
        title_data[title_tag] = utils.clean_value(new_stop.contents[0], encoding)
    # Then find all blocks and add them in
    for tr in schedule_data.find_all('tr'):
        data['blocks'].append(schedule_block(tr, encoding, title_data))
    return data

def schedule_block(block_data, encoding, title_data):
    data = utils.parse_page(block_data, ['blockid'], encoding)
    data['block_id'] = data.pop('blockid', None)
    data['stop_schedules'] = []
    for new_stop in block_data.find_all('stop'):
        ss = stop_schedule(new_stop, encoding)
        ss['title'] = title_data[ss['stop_tag']]
        data['stop_schedules'].append(ss)
    return data

def stop_schedule(stop_data, encoding):
    args = ['tag', 'epochtime']
    data = utils.parse_page(stop_data, args, encoding)
    data['stop_tag'] = data.pop('tag', None)
    data['epoch_time'] = data.pop('epochtime', None)
    time_data = stop_data.contents[0]
    data['time'] = utils.clean_value(time_data, encoding, datetime_format=datetime_format)
    if data['time'] == '--':
        data['time'] = None
    return data
