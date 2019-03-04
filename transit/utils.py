from datetime import datetime
import re

from transit.exceptions import TransitException

def check_args(value, valid_types, allow_none=False, is_list=False, regex=None):
    '''
    Check arguments and throw exceptions when needed
    value       :   Value to check against types
    valid_types :   Valid types which will not throw exceptions
    allow_none  :   Allow None value
    is_list     :   Check that value is list, and then check valid_types against items in list
    regex       :   If value is str, check against regex
    '''
    if allow_none and value is None:
        return

    if is_list:
        if not isinstance(value, list):
            raise TransitException("Invalid value:%s, must be list type" % value)
        for item in value:
            if not isinstance(item, tuple(valid_types)):
                raise TransitException("Invalid value:%s, not one of %s" % (item, valid_types))
            if isinstance(item, str) and regex is not None:
                checker = re.compile(regex)
                if not checker.match(item):
                    raise TransitException("Invalid value:%s, does not match"
                                           " regex %s" % (item, regex))
    elif not isinstance(value, tuple(valid_types)):
        raise TransitException("Invalid value:%s, not one of %s" % (value, valid_types))

    if isinstance(value, str) and regex is not None:
        checker = re.compile(regex)
        if not checker.match(value):
            raise TransitException("Invalid value:%s, does not match regex %s" % (value, regex))

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

    if datetime_format:
        try:
            return datetime.strptime(value, datetime_format)
        except ValueError:
            pass
    else:
        # Assume its a string
        return value.strip().rstrip('\n').lstrip('\n').strip()
    return value
