from bs4 import BeautifulSoup
import requests

from transit.exceptions import TransitException

def make_request(url):
    '''Check return 200 and not error'''
    headers = {'accept-encoding' : 'gzip, deflate'}
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        raise TransitException("URL:%s does not return 200" % url)

    soup = BeautifulSoup(r.text)
    error = soup.find('error')
    if error:
        raise TransitException("URL:%s returned error:%s" % (url, error.string))
    # Get encoding from top of XML data
    contents = soup.contents
    if str(contents[0]) == '\n':
        del contents[0]
    encoding = str(soup.contents[0].split('encoding')[1])
    encoding = encoding.lstrip('="').rstrip('"')
    return soup, encoding

def pretty_strip(data, encoding):
    s = data.string.encode(encoding)
    s = s.lstrip('\n').strip('\n')
    s = s.lstrip(' ').rstrip(' ')
    s = s.lstrip('\n').strip('\n')
    s = s.lstrip(' ').rstrip(' ')
    return s
