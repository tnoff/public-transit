class VehicleLocation(object):
    def __init__(self, vehicle_id, heading, latitude, longitude, route_tag,
                 sec_since_report, speed_km_hr, predictable):
        self.id = int(vehicle_id.encode('utf-8'))
        self.heading = heading.encode('utf-8')
        self.latitude = float(latitude.encode('utf-8'))
        self.longitude = float(longitude.encode('utf-8'))
        self.route_tag = route_tag.encode('utf-8')
        self.seconds_since_last_report = int(sec_since_report.encode('utf-8'))
        self.speed_km_hr = float(speed_km_hr.encode('utf-8'))
        self.predictable = False
        if predictable.encode('utf-8') == "true":
            self.predictable = True

    def __repr__(self):
        return '%s:%s-%s' % (self.id, self.latitude, self.longitude)
