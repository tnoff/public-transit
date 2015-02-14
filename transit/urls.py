main_url = "http://webservices.nextbus.com/service/publicXMLFeed"

# API URLS
agency = {
    'list' : main_url + '?command=agencyList',
}

route = {
    'list' : main_url + '?command=routeList&a=%s'
}
