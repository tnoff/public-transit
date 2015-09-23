from datetime import datetime

datetime_default = '%a, %b %d %H:%M:%S %Z %Y'

def pretty_time(minutes, seconds):
    stringy = ''
    if minutes < 10:
        stringy += '0'
    stringy += '%s:' % str(minutes)
    if seconds < 10:
        stringy += '0'
    stringy += '%s' % str(seconds)
    return stringy

def parse_data(data, key_name, encoding, datetime_format=datetime_default):
    # some values are part of the object such as
    # .. <foo bar=1>
    # others are placed within
    # .. <foo><bar>1</bar></foo>
    # handle either here
    value = data.get(key_name)
    if value is None:
        value = data.find(key_name)
        if value is None:
            return None
        try:
            value = value.contents[0]
        except IndexError:
            return None

    value = value.encode(encoding)

    number = convert_number(value)
    if number:
        return number
    date = convert_datetime(value, datetime_format)
    if date:
        return date
    bol = convert_boolean(value)
    if bol:
        return bol

    return value

def convert_number(value):
    # convert to either int or float
    try:
        float_value = float(value)
    except ValueError:
        return None
    try:
        int_value = int(value)
    except ValueError:
        return float_value

    # if int and float same, is int
    # int(3.0) == float(3.0)
    if int_value == float_value:
        return int_value
    return float_value

def convert_datetime(value, datetime_format):
    try:
        return datetime.strptime(value, datetime_format)
    except ValueError:
        return None

def convert_boolean(value):
    if "true" in value.lower() or "false" in value.lower():
        return bool(value)
    return None
