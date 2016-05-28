from transit import utils

datetime_format = '%a %b %d %Y %I:%M %p %Z'

def service_advisory(bsa_data, encoding):
    args = ['id', 'station', 'type', 'description', 'posted', 'expires']
    return utils.parse_page(bsa_data, args, encoding,
                            datetime_format=datetime_format)
