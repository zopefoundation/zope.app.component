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

$Id: hooks.py,v 1.2 2002/12/25 14:12:45 jim Exp $
"""
from zope.component.interfaces import IServiceService
from zope.app.interfaces.services.service \
     import IServiceManagerContainer
from zope.component.exceptions import ComponentLookupError
from zope.proxy.context import getWrapperContainer, ContextWrapper
from zope.component import getServiceManager
from zope.component.exceptions import ComponentLookupError
from zope.component.service import serviceManager
from zope.proxy.introspection import removeAllProxies
from zope.security.proxy import trustedRemoveSecurityProxy

def getServiceManager_hook(context):
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
                name="++etc++Services",
                )

        context = getWrapperContainer(context)

    return serviceManager
