from datetime import datetime

def parse_page(page_data, arguments, encoding, datetime_format=None):
    data = {}
    for arg in arguments:
        value = parse_data(page_data, arg)
        data[arg] = clean_value(value, encoding, datetime_format=datetime_format)
    return data

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
    if value is None:
        return None

    new_value = value.encode(encoding)

    if datetime_format:
        try:
            new_value = datetime.strptime(new_value, datetime_format)
            return new_value
        except ValueError:
            pass
    return new_value
