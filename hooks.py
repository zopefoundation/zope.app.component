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
__docformat__ = 'restructuredtext'

import zope.component
from zope.app.component.interfaces import ISite
from zope.component.exceptions import ComponentLookupError
from zope.security.proxy import removeSecurityProxy
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.location.interfaces import ILocation
from zope.app.location import locate
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
    #services = serviceManager

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

def adapter_hook(interface, object, name='', default=None):
    try:
        return siteinfo.adapter_hook(interface, object, name, default)
    except ComponentLookupError:
        return default


def setHooks():
    # Hook up a new implementation of looking up views.
    zope.component.adapter_hook.sethook(adapter_hook)

def resetHooks():
    # Reset hookable functions to original implementation.
    zope.component.adapter_hook.reset()
    
