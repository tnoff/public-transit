from datetime import datetime

def pretty_time(minutes, seconds):
    stringy = ''
    if minutes < 10:
        stringy += '0'
    stringy += '%s:' % str(minutes)
    if seconds < 10:
        stringy += '0'
    stringy += '%s' % str(seconds)
    return stringy

def parse_data(data, key_name):
    # some values are part of the object such as
    # .. <foo bar=1>
    # others are placed within
    # .. <foo><bar>1</bar></foo>
    # handle either here

    # sometimes its as easy as a get
    value = data.get(key_name)
    # most of the time you have to find
    if value is None:
        value = data.find(key_name)
        if value is None:
            return None
        try:
            value = value.contents[0]
        except IndexError:
            return None
    return value
def clean_value(value, encoding, datetime_format=None):
    # clean string to whatever type it should be
    if value is None:
        return None
    new_value = value.encode(encoding)

    # try to make it a datetime if format given first
    if datetime_format:
        try:
            new_value = datetime.strptime(new_value, datetime_format)
            return new_value
        except ValueError:
            pass
    return new_value
