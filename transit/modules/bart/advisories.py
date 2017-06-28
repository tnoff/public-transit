from datetime import datetime
from pytz import timezone

from transit import utils

datetime_format = '%a %b %d %Y %I:%M %p'
pacific_timezone = timezone('US/Pacific')

def service_advisory(bsa_data, encoding):
    args = ['id', 'station', 'type', 'description', 'posted', 'expires']
    page_data = utils.parse_page(bsa_data, args, encoding)
    # so this is a weird thing, python datetime doesnt support natively calling
    # .. PDT or PST, but the work around isnt that bad
    # .. strip the end PDT or PST off the end of the string, pass the rest
    # .. in to get the datetime, then adjust to Pacific time (since bart is always pacific)
    if page_data['posted'] is not None:
        time_suffix = page_data['posted'][-4:].rstrip(' ').lstrip(' ')
        assert time_suffix == 'PST' or time_suffix == 'PDT', \
                'Invalid type suffix, time to rewrite code'
        posted = datetime.strptime(page_data['posted'][0:-4], datetime_format)
        page_data['posted'] = datetime(posted.year, posted.month, posted.day,
                                       posted.hour, posted.minute, posted.second,
                                       0, pacific_timezone)
    if page_data['expires'] is not None:
        time_suffix = page_data['expires'][-4:].rstrip(' ').lstrip(' ')
        assert time_suffix == 'PST' or time_suffix == 'PDT', \
                'Invalid type suffix, time to rewrite code'
        expires = datetime.strptime(page_data['expires'][0:-4], datetime_format)
        page_data['expires'] = datetime(expires.year, expires.month, expires.day,
                                        expires.hour, expires.minute, expires.second,
                                        0, pacific_timezone)
    page_data['id'] = int(page_data['id'])
    page_data['station'] = page_data['station'].lower()
    page_data['type'] = page_data['type'].lower()
    return page_data
