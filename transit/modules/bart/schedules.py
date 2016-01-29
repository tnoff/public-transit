from transit.common import utils as common_utils

def schedule(schedule_data, encoding):
    args = ['id', 'effectivedate']
    data = common_utils.parse_page(schedule_data, args, encoding)
    data['effective_date'] = data.pop('effectivedate', None)
    return data

def schedule_fare(schedule_data, encoding):
    args = ['origin', 'destination', 'sched_num']
    data = common_utils.parse_page(schedule_data, args, encoding)
    data['schedule_number'] = data.pop('sched_num', None)

    # this page is a little strange, this is within another part
    trip_data = schedule_data.find('trip')
    fare_value = common_utils.parse_data(trip_data, 'fare')
    data['fare'] = common_utils.clean_value(fare_value, encoding)
    discount = trip_data.find('discount')
    clipper = common_utils.parse_data(discount, 'clipper')
    data['discount'] = common_utils.clean_value(clipper, encoding)
    return data
