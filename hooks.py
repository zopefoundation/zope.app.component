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
"""Hooks for getting and setting a site in the thread global namespace.

$Id$
"""
from zope.component import getService
from zope.component.interfaces import IServiceService
from zope.app.site.interfaces import ISite
from zope.component.service import serviceManager
from zope.component.exceptions import ComponentLookupError
from zope.security.proxy import removeSecurityProxy
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.location.interfaces import ILocation
from zope.app.location import locate
from zope.component.servicenames import Presentation
from zope.interface import Interface
from zope.component.servicenames import Adapters
import warnings
import zope.thread

class read_property(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, inst, cls):
        if inst is None:
            return self

        return self.func(inst)

class SiteInfo(zope.thread.local):
    site = None
    services = serviceManager

    def adapter_hook(self):
        services = self.services
        adapters = services.getService(Adapters)
        adapter_hook = adapters.adapter_hook
        self.adapter_hook = adapter_hook
        return adapter_hook
    
    adapter_hook = read_property(adapter_hook)

siteinfo = SiteInfo()

def setSite(site=None):
    if site is None:
        services = serviceManager
    else:

        # We remove the security proxy because there's no way for
        # untrusted code to get at it without it being proxied again.

        # We should really look look at this again though, especially
        # once site managers do less.  There's probably no good reason why
        # they can't be proxied.  Well, except maybe for performance.
        
        site = removeSecurityProxy(site)
        services = site.getSiteManager()

    siteinfo.site = site
    siteinfo.services = services
    try:
        del siteinfo.adapter_hook
    except AttributeError:
        pass
    
def getSite():
    return siteinfo.site
    
def getServices_hook(context=None):

    if context is None:
        return siteinfo.services

    # Deprecated support for a context that isn't adaptable to
    # IServiceService.  Return the default service manager.
    try:


        # We remove the security proxy because there's no way for
        # untrusted code to get at it without it being proxied again.

        # We should really look look at this again though, especially
        # once site managers do less.  There's probably no good reason why
        # they can't be proxied.  Well, except maybe for performance.


        return removeSecurityProxy(IServiceService(context,
                                                   serviceManager))
    except ComponentLookupError:
        return serviceManager

def adapter_hook(interface, object, name='', default=None):
    try:
        return siteinfo.adapter_hook(interface, object, name, default)
    except ComponentLookupError:
        return default
    
def queryView(object, name, request, default=None,
              providing=Interface, context=None):
    views = getService(Presentation, context)
    view = views.queryView(object, name, request, default=default,
                           providing=providing)
    if ILocation.providedBy(view):
        locate(view, object, name)

    return view
