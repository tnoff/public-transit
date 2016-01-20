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
    while True:
        if str(contents[0]) == '\n':
            del contents[0]
        else:
            break
    encoding = str(soup.contents[0].split('encoding')[1])
    encoding = encoding.lstrip('="').rstrip('"')
    # check for errors
    error = soup.find('error')
    if error:
        error_string = error.string
        if not error_string:
            # bart gives error in "details"
            error_string = error.find('details').string.encode(encoding)
        raise TransitException("URL:%s returned error:%s" % (url, error_string))
    return soup, encoding