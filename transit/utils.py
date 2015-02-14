from bs4 import BeautifulSoup
import requests

def make_request(url):
    '''Check return 200 and not error'''
    r = requests.get(url)

    if r.status_code != 200:
        raise Exception("URL:%s does not return 200" % url)

    soup = BeautifulSoup(r.text)
    error = soup.find('error')
    if error:
        raise Exception("URL:%s returned error:%s" % (url, error.string))

    return soup
