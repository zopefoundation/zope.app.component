# BBB: Goes away in 3.3
from zope.component.exceptions import ComponentLookupError


def queryNextService(context, name, default=None):
    try:
        return getNextService(context, name)
    except ComponentLookupError:
        return default

def getNextService(context, name):
    """Returns the service with the given name from the next service manager.
    """
    from zope.component.bbb.service import IService
    from zope.app.component import getNextSiteManager
    return getNextSiteManager(context).queryUtility(IService, name)
