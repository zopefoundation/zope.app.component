##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""

$Id$
"""

from zope.component import getService, getAdapter
from zope.component.interfaces import IServiceService
from zope.app.site.interfaces import ISite
from zope.component.service import serviceManager
from zope.component.exceptions import ComponentLookupError
from zope.proxy import removeAllProxies
from zope.security.proxy import trustedRemoveSecurityProxy
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.location.interfaces import ILocation
from zope.app.location import locate
from zope.component.servicenames import Presentation
from zope.interface import Interface
import warnings
import zope.thread

siteinfo = zope.thread.local()

def setSite(site=None):
    if site is None:
        siteinfo.services = None
    else:
        siteinfo.services = trustedRemoveSecurityProxy(site.getSiteManager())

def getSite():
    try:
        services = siteinfo.services
    except AttributeError:
        services = siteinfo.services = None
        
    if services is None:
        return None

    return services.__parent__
    

def getServices_hook(context=None):

    if context is None:
        try:
            services = siteinfo.services
        except AttributeError:
            services = siteinfo.services = None

        if services is None:
            return serviceManager

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
    views = getService(Presentation, context)
    view = views.queryView(object, name, request, default=default,
                           providing=providing)
    if ILocation.providedBy(view):
        locate(view, object, name)

    return view
