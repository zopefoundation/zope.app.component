##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Support for delegation among service managers

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.component.exceptions import ComponentLookupError
from zope.component.service import serviceManager
from zope.component.interfaces import IServiceService
from zope.app.site.interfaces import ISite, ISiteManager
from zope.testing.cleanup import addCleanUp
from zope.app.component.hooks import setSite
from zope.component.service import IGlobalServiceManager
from zope.security.proxy import removeSecurityProxy

# placeful service manager convenience tools

# TODO: <SteveA> What we really want here is
#
# getLocalServices(context)
# # if context is contained in a service manager, returns the service manager
# # if context is a service manager, returns context
# # otherwise, raises ComponentLookupError('Services')
#
# getLocalService(context, name):
# # Returns the local service with that name
# # This is the same as getService, so why bother? parity.
# 
# getNextServices(context, name):
# # looks up the local service manager, then gets the next higher one
# # and returns it
#
# getNextService(context, name):
# # Returns the next service manager's service with that name.



##def getLocalService(context, name):
##    service = queryLocalService(context, name)
##    if service is None:
##        raise ComponentLookupError('service', name)
##    return service
##
##def queryLocalService(context, name, default=None):
##    try:
##        sm = getLocalServices(context)
##        return sm.getService(name)
##    except ComponentLookupError:
##        return default

def queryNextService(context, name, default=None):
    try:
        return getNextService(context, name)
    except ComponentLookupError:
        return default

def getNextService(context, name):
    """Returns the service with the given name from the next service manager.
    """
    return getNextServices(context).getService(name)

def getNextServices(context):
    """Returns the next service manager to the one that contains `context`.
    """
    services = getLocalServices(context).next
    if IGlobalServiceManager.providedBy(services):
        services = removeSecurityProxy(services)
    return services

def queryNextServices(context, default=None):
    try:
        return getNextServices(context)
    except ComponentLookupError:
        return default

def queryLocalServices(context, default=None):
    try:
        return getLocalServices(context)
    except ComponentLookupError:
        return default

def getLocalServices(context):
    """Returns the service manager that contains `context`.

    If `context` is a local service, returns the service manager that
    contains that service. If `context` is a service manager, returns `context`.

    Otherwise, raises ``ComponentLookupError('Services')``
    """

    # IMPORTANT
    #
    # This is not allowed to use any services to get its job done!

    while not (context is None or
               ISiteManager.providedBy(context)):
        context = getattr(context, '__parent__', None)
    if context is None:
        raise ComponentLookupError('Services')
    else:
        return context

def serviceServiceAdapter(ob):
    """An adapter ILocation -> IServiceService.

    The ILocation is interpreted flexibly, we just check for
    ``__parent__``.
    """
    current = ob
    while True:
        if ISite.providedBy(current):
            return current.getSiteManager()
        current = getattr(current, '__parent__', None)
        if current is None:
            raise ComponentLookupError("Could not adapt %r to"
                                       " IServiceService" % (ob, ))


def threadSiteSubscriber(event):
    """A subscriber to BeforeTraverseEvent

    Sets the 'site' thread global if the object traversed is a site.
    """
    if ISite.providedBy(event.object):
        setSite(event.object)


def clearThreadSiteSubscriber(event):
    """A subscriber to EndRequestEvent

    Cleans up the site thread global after the request is processed.
    """
    clearSite()

# Clear the site thread global
clearSite = setSite

addCleanUp(clearSite)
