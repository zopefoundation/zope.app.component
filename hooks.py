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

$Id: hooks.py,v 1.15 2004/02/09 01:11:59 anthony Exp $
"""

from zope.component import getService
from zope.component.interfaces import IServiceService
from zope.component.exceptions import ComponentLookupError
from zope.component.servicenames import Adapters
from zope.app.interfaces.services.service import ISite
from zope.component.service import serviceManager
from zope.proxy import removeAllProxies
from zope.security.proxy import trustedRemoveSecurityProxy
from zope.app.traversing import IContainmentRoot
from zope.app.interfaces.location import ILocation
from zope.app.location import locate
from zope.component.servicenames import Presentation
from zope.interface import Interface

def getServiceManager_hook(context, local=False, recurse=False):

    if context is None:
        return serviceManager

    clean_context = removeAllProxies(context)

    # if the context is actually a service or site manager...
    if IServiceService.isImplementedBy(clean_context):
        return trustedRemoveSecurityProxy(context)

    elif (ISite.isImplementedBy(clean_context)):
        return trustedRemoveSecurityProxy(context.getSiteManager())
    else:
        container = getattr(context, '__parent__', None)
        if container is None:
            if local:
                # Check to make sure that when we run out of context, we
                # have a root object:
                if not IContainmentRoot.isImplementedBy(context):
                    raise TypeError("Not enough context to get next "
                                    "site manager")

            # Fall back to global:
            sm = serviceManager
        else:
            # We have a container, so context is a wrapper.  We still
            # don't have a site manager, so try again, recursively:
            sm = getServiceManager_hook(container, local, True)

    return sm


def queryView(object, name, request, default=None, context=None,
              providing=Interface):
    if context is None:
        context = object
    views = getService(context, Presentation)
    view = views.queryView(object, name, request, default=default,
                           providing=providing)
    if ILocation.isImplementedBy(view):
        locate(view, object, name)

    return view
