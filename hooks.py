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

$Id: hooks.py,v 1.6 2003/05/23 17:52:33 jim Exp $
"""

from zope.component import getService
from zope.component.interfaces import IServiceService
from zope.component.exceptions import ComponentLookupError
from zope.component.servicenames import Adapters
from zope.app.interfaces.services.service import IServiceManagerContainer
from zope.proxy.context import getWrapperContainer, ContextWrapper
from zope.proxy.context import isWrapper, getWrapperData
from zope.component.service import serviceManager
from zope.proxy.introspection import removeAllProxies
from zope.security.proxy import trustedRemoveSecurityProxy
from zope.app.traversing import IContainmentRoot

## alog=open('alog','w')
## slog=open('slog','w')
## swlog=open('swlog','w')
## sulog=open('sulog','w')
## sutblog=open('sutblog','w')
## nlog=open('nlog','w')

## import sys, traceback




def getServiceManager_hook(context, local=False, recurse=False):

    
    # XXX Uh, there's this special case for context being none. :(
    if context is None:
##         if not recurse:
##             slog.write('n')
##             nlog.write('\n')
##             f = sys._getframe(1)
##             nlog.write("%s\n" % context.__class__)
##             nlog.write(''.join(traceback.format_stack(sys._getframe(1),
##                                                          5)))
##             nlog.write("\n")

        return serviceManager


    data = None
    wrapped = isWrapper(context)
    if wrapped:
        data = getWrapperData(context, create=True)
##         unwrapped = removeAllProxies(context)
##         oid = id(unwrapped)
##         did = id(data)
##         if not recurse:
##             swlog.write("%s %s %s\n" %
##                         (context.__class__.__name__, oid, did))
        cached = data.get('zope.app.component.hooks.sm')
        if cached is not None:
##             if not recurse:
##                 slog.write('h')
            return cached
##         else:
##             if not recurse:
##                 slog.write('m')
##     else:
##         if not recurse:
##             sulog.write("%s.%s\n" %
##                         (context.__class__.__module__,
##                          context.__class__.__name__))
##             f = sys._getframe(1)
##             avoid = "src/zope/app/component/hooks.py"
##             if (1 or f.f_back.f_code.co_filename != avoid
##                 ):
##                 sutblog.write("%s\n" % context.__class__)
##                 sutblog.write(''.join(traceback.format_stack(sys._getframe(1),
##                                                              5)))
##                 sutblog.write("\n")
##             slog.write('u')
        

    clean_context = removeAllProxies(context)

    # if the context is actually a service or service manager...
    if IServiceService.isImplementedBy(clean_context):
        sm = trustedRemoveSecurityProxy(context)

    elif (IServiceManagerContainer.isImplementedBy(clean_context) and
        clean_context.hasServiceManager()
        ):
        sm = ContextWrapper(
            trustedRemoveSecurityProxy(context.getServiceManager()),
            context,
            name="++etc++site",
            )
    else:
        container = getWrapperContainer(context)
        if container is None:
            if local:
                # Check to make sure that when we run out of context, we
                # have a root object:
                if not IContainmentRoot.isImplementedBy(context):
                    raise TypeError("Not enough context to get next "
                                    "service manager")

            # Fall back to global:
            sm = serviceManager
        else:
            # We have a container, so context is a wrapper.  We still
            # don't have a service manager, so try again, recursively:
            sm = getServiceManager_hook(container, local, True)

    # Now cache what we found, cause we might look for it again:
    if wrapped:
        data['zope.app.component.hooks.sm'] = sm

    return sm

def queryNamedAdapter(object, interface, name, default=None, context=None):
    if context is None:
        context = object

    wrapped = isWrapper(context)
##     alog.write("%s %s.%s %s.%s\n" % (wrapped,
##                                context.__class__.__module__,
##                                context.__class__.__name__,
##                                interface.__module__,
##                                interface.__name__,
##                                ))
    if wrapped:
        data = getWrapperData(context, create=True)
        adapters = data.get('zope.app.component.hooks.adapters')
        if adapters is None:
            try:
                adapters = getService(context, Adapters)
            except ComponentLookupError:
                # Oh blast, no adapter service. We're probably just
                # running from a test
                return default
            data['zope.app.component.hooks.adapters'] = adapters
    else:
        try:
            adapters = getService(context, Adapters)
        except ComponentLookupError:
            # Oh blast, no adapter service. We're probably just
            # running from a test
            return default

    return adapters.queryNamedAdapter(object, interface, name, default)
