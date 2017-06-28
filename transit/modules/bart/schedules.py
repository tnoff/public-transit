from datetime import datetime

from transit import utils

# DATETIME_FORMAT = "01/01/2014 01:00 PM"
DATETIME_FORMAT = "%m/%d/%Y %I:%M %p"

def schedule(schedule_data, encoding):
    args = ['id', 'effectivedate']
    data = utils.parse_page(schedule_data, args, encoding)
    effective_date = data.pop('effectivedate', None)
    data['effective_date'] = datetime.strptime(effective_date,
                                               DATETIME_FORMAT)
    data['id'] = int(data.pop('id'))
    return data

def schedule_fare(schedule_data, encoding):
    args = ['origin', 'destination', 'sched_num']
    data = utils.parse_page(schedule_data, args, encoding)
    schedule_number = data.pop('sched_num', None)
    if schedule_number:
        data['schedule_number'] = int(schedule_number)
    data['origin'] = data.pop('origin').lower()
    data['destination'] = data.pop('destination').lower()

    # this page is a little strange, this is within another part
    trip_data = schedule_data.find('trip')
    fare_value = utils.parse_data(trip_data, 'fare')
    data['fare'] = float(utils.clean_value(fare_value, encoding))
    discount = trip_data.find('discount')
    clipper = utils.parse_data(discount, 'clipper')
    data['discount'] = float(utils.clean_value(clipper, encoding))
    data['clipper'] = float(utils.clean_value(clipper, encoding))
    return data
