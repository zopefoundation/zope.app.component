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

$Id: hooks.py,v 1.5 2003/05/01 19:35:07 faassen Exp $
"""
from zope.component.interfaces import IServiceService
from zope.app.interfaces.services.service import IServiceManagerContainer
from zope.proxy.context import getWrapperContainer, ContextWrapper
from zope.component.service import serviceManager
from zope.proxy.introspection import removeAllProxies
from zope.security.proxy import trustedRemoveSecurityProxy
from zope.app.traversing import IContainmentRoot

def getServiceManager_hook(context, local=False):
    """
    context based lookup, with fallback to component architecture
    service manager if no service manager found within context
    """
    while context is not None:
        clean_context = removeAllProxies(context)

        # if the context is actually a service or service manager...
        if IServiceService.isImplementedBy(clean_context):
            return trustedRemoveSecurityProxy(context)

        if (IServiceManagerContainer.isImplementedBy(clean_context) and
            clean_context.hasServiceManager()
            ):
            return ContextWrapper(
                trustedRemoveSecurityProxy(context.getServiceManager()),
                context,
                name="++etc++site",
                )

        container = getWrapperContainer(context)
        if container is None:
            if local:
                # Check to make sure that when we run out of context, we
                # have a root object:
                if not IContainmentRoot.isImplementedBy(context):
                    raise TypeError("Not enough context to get next "
                                    "service manager")
                break
            
        context = container

    return serviceManager
