##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""

import warnings
from zope.component import getService, getAdapter, queryAdapter
from zope.component.interfaces import IServiceService
from zope.app.site.interfaces import ISite
from zope.component.service import serviceManager
from zope.component.exceptions import ComponentLookupError
from zope.proxy import removeAllProxies
from zope.security.proxy import trustedRemoveSecurityProxy
from zope.app.traversing import IContainmentRoot
from zope.app.location.interfaces import ILocation
from zope.app.location import locate
from zope.component.servicenames import Presentation
from zope.interface import Interface
from zope.thread import thread_globals

def setSite(site=None):
    if site is None:
        services = None
    else:
        services = trustedRemoveSecurityProxy(site.getSiteManager())

    thread_globals().services = services

def getSite():
    services = thread_globals().services
    if services is None:
        return None
    return services.__parent__
    

def getServices_hook(context=None):

    if context is None:
        try:
            services = thread_globals().services
        except AttributeError:
            thread_globals().services = services = None
            
        if services is None:
            return serviceManager
        else:
            return services

    try:
        # This try-except is just backward compatibility really
        return trustedRemoveSecurityProxy(getAdapter(context, IServiceService))
    except ComponentLookupError:
        # Deprecated support for a context that isn't adaptable to
        # IServiceService.  Return the default service manager.
        ## warnings.warn("getServices' context arg must be None or"
        ##               "  adaptable to IServiceService.",
        ##               DeprecationWarning, warningLevel())
        return serviceManager


def queryView(object, name, request, default=None,
              providing=Interface, context=None):
    # XXX test
    #if context is None:
    #    context = object
    views = getService(context, Presentation)
    view = views.queryView(object, name, request, default=default,
                           providing=providing)
    if ILocation.providedBy(view):
        locate(view, object, name)

    return view
