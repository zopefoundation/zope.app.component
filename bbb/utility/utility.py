##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""Local utility service implementation.

Besides being functional, this module also serves as an example of
creating a local service; see README.txt.

$Id$
"""
from persistent.interfaces import IPersistent
import zope.interface
import zope.interface.adapter
from zope.component.utility import UtilityService, GlobalUtilityService
from zope.security.proxy import removeSecurityProxy

import zope.app.site.interfaces
from zope.app import zapi
from zope.app.adapter.adapter import LocalAdapterService
from zope.app.component.localservice import queryNextService
from zope.app.registration.registration import ComponentRegistration
from zope.app.utility.interfaces import ILocalUtilityService
from zope.app.utility.interfaces import IUtilityRegistration

class LocalUtilityService(UtilityService, LocalAdapterService):
    """Local Utility Service
    """

    serviceType = zapi.servicenames.Utilities

    zope.interface.implementsOnly(
        ILocalUtilityService,
        zope.app.site.interfaces.ISimpleService,
        zope.app.site.interfaces.IBindingAware,
        IPersistent # used for IKeyReference adaption
        )


    def queryRegistrations(self, name, interface):
        return self.queryRegistrationsFor(
            UtilityRegistration(name, interface, None)
            )

    def getLocalUtilitiesFor(self, interface):
        # This method is deprecated and is temporarily provided for
        # backward compatability
        from zope.app import zapi
        from zope.app.component.localservice import getNextService
        next = getNextService(self, zapi.servicenames.Utilities)
        next_utils = dict(next.getUtilitiesFor(interface))
        for name, util in self.getUtilitiesFor(interface):
            if next_utils.get(name) != util:
                yield name, util


    def _updateAdaptersFromLocalData(self, adapters):
        LocalAdapterService._updateAdaptersFromLocalData(self, adapters)
        
        for required, stacks in self.stacks.iteritems():
            if required is None:
                required = Default
            radapters = adapters.get(required)

            for key, stack in stacks.iteritems():
                registration = stack.active()
                if registration is not None:
                    key = True, key[1], '', key[3]

                    # Needs more thought:
                    # We have to remove the proxy because we're
                    # storing the value amd we can't store proxies.
                    # (Why can't we?)  we need to think more about
                    # why/if this is truly safe
                    
                    radapters[key] = radapters.get(key, ()) + (
                        removeSecurityProxy(registration.factory), )



class UtilityRegistration(ComponentRegistration):
    """Utility component registration for persistent components

    This registration configures persistent components in packages to
    be utilities.
    """
    zope.interface.implements(IUtilityRegistration)

    serviceType = zapi.servicenames.Utilities

    ############################################################
    # To make adapter code happy. Are we going too far?
    #
    required = zope.interface.adapter.Null
    with = ()
    provided = property(lambda self: self.interface)
    factory = property(lambda self: self.component)
    #
    ############################################################

    def __init__(self, name, interface, component, permission=None):
        super(UtilityRegistration, self).__init__(component, permission)
        self.name = name
        self.interface = interface

    def usageSummary(self):
        # Override IRegistration.usageSummary()
        s = self.getInterface().getName()
        if self.name:
            s += " registered as '%s'" % self.name
        s += ", implemented by %s" %self.component.__class__.__name__
        s += " '%s'"%zapi.name(self.component)
        return s

    def getInterface(self):
        # ComponentRegistration calls this when you specify a
        # permission; it needs the interface to create a security
        # proxy for the interface with the given permission.
        return self.interface



_marker = object()

def getNextUtility(context, interface, name=''):
    """Get the next available utility.

    If no utility was found, a `ComponentLookupError` is raised.
    """
    util = queryNextUtility(context, interface, name, _marker)
    if util is _marker:
        raise ComponentLookupError, \
              "No more utilities for %s, '%s' have been found." %(interface,
                                                                  name)
    return util


def queryNextUtility(context, interface, name='', default=None):
    """Query for the next available utility.

    Find the next available utility providing `interface` and having the
    specified name. If no utility was found, return the specified `default`
    value.

    It is very important that this method really finds the next utility and
    does not abort, if the utility was not found in the next utility service.

    Let's start out by declaring a utility interface and an implementation:

      >>> from zope.interface import Interface, implements
      >>> class IAnyUtility(Interface):
      ...     pass
      
      >>> class AnyUtility(object):
      ...     implements(IAnyUtility)
      ...     def __init__(self, id):
      ...         self.id = id
      
      >>> any1 = AnyUtility(1)
      >>> any1next = AnyUtility(2)

    Now that we have the utilities, let's register them:

      >>> testingNextUtility(any1, any1next, IAnyUtility)

    The next utility of `any1` ahould be `any1next`:

      >>> queryNextUtility(any1, IAnyUtility) is any1next
      True

    But `any1next` does not have a next utility, so the default is returned:

      >>> queryNextUtility(any1next, IAnyUtility) is None
      True

    """    
    util = _marker
    while util is _marker:
        utilservice = queryNextService(context, zapi.servicenames.Utilities)
        if utilservice is None:
            return default
        util = utilservice.queryUtility(interface, name, _marker)
        context = utilservice
        
    return util


def testingNextUtility(utility, nextutility, interface, name='',
                       service=None, nextservice=None):
    """Provide a next utility for testing.

    Since utilities must be registered in services, we really provide a next
    utility service in which we place the next utility. If you do not pass in
    any services, they will be created for you.

    For a simple usage of this function, see the doc test of
    `queryNextUtility()`. Here is a demonstration that passes in the services
    directly and ensures that the `__parent__` attributes are set correctly.

    First, we need to create a utility interface and implementation:

      >>> from zope.interface import Interface, implements
      >>> class IAnyUtility(Interface):
      ...     pass
      
      >>> class AnyUtility(object):
      ...     implements(IAnyUtility)
      ...     def __init__(self, id):
      ...         self.id = id
      
      >>> any1 = AnyUtility(1)
      >>> any1next = AnyUtility(2)

    Now we create a special utility service that can have a location:

      >>> UtilityService = type('UtilityService', (GlobalUtilityService,),
      ...                       {'__parent__': None})

    Let's now create one utility service

      >>> utils = UtilityService()

    and pass it in as the original utility service to the function:

      >>> testingNextUtility(any1, any1next, IAnyUtility, service=utils)
      >>> any1.__parent__ is utils
      True
      >>> utilsnext = any1next.__parent__
      >>> utils.__parent__.next.data['Utilities'] is utilsnext
      True

    or if we pass the current and the next utility service:

      >>> utils = UtilityService()
      >>> utilsnext = UtilityService()
      >>> testingNextUtility(any1, any1next, IAnyUtility,
      ...                    service=utils, nextservice=utilsnext)
      >>> any1.__parent__ is utils
      True
      >>> any1next.__parent__ is utilsnext
      True
    
    """
    UtilityService = type('UtilityService', (GlobalUtilityService,),
                          {'__parent__': None})
    if service is None:
        service = UtilityService()
    if nextservice is None:
        nextservice = UtilityService()
    from zope.app.component.localservice import testingNextService
    testingNextService(service, nextservice, zapi.servicenames.Utilities)

    service.provideUtility(interface, utility, name)
    utility.__parent__ = service
    nextservice.provideUtility(interface, nextutility, name)
    nextutility.__parent__ = nextservice
