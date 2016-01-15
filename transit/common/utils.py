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
