class Agency(object):
    def __init__(self, tag, title, region):
        self.tag = tag.encode('utf-8')
        self.title = title.encode('utf-8')
        self.region = region.encode('utf-8')

    def __repr__(self):
        return '%s - %s - %s' % (self.title, self.region, self.tag)
