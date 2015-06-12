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

predictions = {
    # a : agency_tag, stopId : stop id
    'stop' : main_url + '?command=predictions&a=%s&stopId=%s',
    # a : agency_tag, stopId : stop id, routeTag: route_tag
    'route' : main_url + '?command=predictions&a=%s&stopId=%s&routeTag=%s',
    # a : agency_tag, stops=RouteTag|StopTag
    'multi' : {'url' : main_url + '?command=predictionsForMultiStops&a=%s',
               'suffix' : '&stops=%s|%s',},

}

schedule = {
    # a : agency_tag, r : route_tag
    'show' : main_url + '?command=schedule&a=%s&r=%s'
}

vehicle = {
    # a : agency_tag, r : route_tag, t : epoch_time_in_msec
    'location' : main_url + '?command=vehicleLocations&a=%s&r=%s&t=%s'
}

message = {
    # a : agency_tag, r: route_tag
    'message' : {'url' : main_url + '?command=messages&a=%s',
                 'suffix' : '&r=%s',}
}
