main_url = "http://webservices.nextbus.com/service/publicXMLFeed"

# API URLS
agency = {
    'list' : main_url + '?command=agencyList',
}

route = {
    # a : agency_tag
    'list' : main_url + '?command=routeList&a=%s',
    # a : agency_tag, r : route_tag
    'show' : main_url + '?command=routeConfig&a=%s&r=%s',
}
