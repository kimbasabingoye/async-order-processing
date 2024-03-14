from enum import Enum

class Services(str, Enum):
    """ Representation of valid services in the system. """
    web_site = 'Make a web site'
    mobile_app = 'Make a mobile app'
    desktop_app = 'Make a desktop app'


def get_service_prices(service: Services):
    if service == Services.web_site:
        return 5000
    elif service == Services.mobile_app:
        return 8000
    else:
        return 10000
    

#print(get_service_prices('Make a web site'))
