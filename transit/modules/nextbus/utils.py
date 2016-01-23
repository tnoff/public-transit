from bs4 import BeautifulSoup
import requests

from transit.exceptions import TransitException

def make_request(url, markup="html.parser"):
    headers = {'accept-encoding' : 'gzip, deflate'}
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        raise TransitException("URL:%s does not return 200" % url)

    soup = BeautifulSoup(r.text, markup)
    # Get encoding from top of XML data
    contents = soup.contents
    if str(contents[0]) == '\n':
        del contents[0]
    encoding = str(soup.contents[0].split('encoding')[1])
    encoding = encoding.lstrip('="').rstrip('"')
    # check for errors
    error = soup.find('error')
    if error:
        # nextbus just gives error message in error
        error_string = error.string
        raise TransitException("URL:%s returned error:%s" % (url, error_string))
    return soup, encoding

def prediction_time(minutes, seconds):
    # nextbus returns 1 min 2 seconds as (1 min, 62 seconds), its kinda weird
    # .. calculate here and return with a nicer datetime
    seconds = seconds - (60 * minutes)
    hours = minutes / 60
    minutes = minutes % 60
    stringy = ''
    if hours > 0:
        stringy += '%s:' % hours
    if minutes < 10:
        stringy += '0'
    stringy += '%s:' % minutes
    if seconds < 10:
        stringy += '0'
    stringy += '%s' % seconds
    return stringy
