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
"""Adapter Service

$Id$
"""
__docformat__ = 'restructuredtext' 

from persistent.dict import PersistentDict
from persistent import Persistent
from zope.app import zapi
from zope.app.registration.registration import NotifyingRegistrationStack
from zope.interface.adapter import adapterImplied, Default
from zope.interface.adapter import Surrogate, AdapterRegistry
from zope.security.proxy import removeSecurityProxy
import sys
import zope.app.component.localservice
import zope.app.container.contained
import zope.app.registration.interfaces
import zope.app.site.interfaces
import zope.app.registration
import zope.component.interfaces
import zope.component.adapter
import zope.interface
import zope.schema
from zope.app.i18n import ZopeMessageIDFactory as _

class LocalSurrogate(Surrogate):
    """Local surrogates

    Local surrogates are transient, rather than persistent.

    Their adapter data are stored in their registry objects.
    """

    def __init__(self, spec, registry):
        Surrogate.__init__(self, spec, registry)
        self.registry = registry
        registry.baseFor(spec).subscribe(self)

    def clean(self):
        spec = self.spec()
        base = self.registry.baseFor(spec)
        ladapters = self.registry.adapters.get(spec)
        if ladapters:
            adapters = base.adapters.copy()
            adapters.update(ladapters)
        else:
            adapters = base.adapters
        self.adapters = adapters
        Surrogate.clean(self)

class LocalAdapterRegistry(AdapterRegistry, Persistent):
    """Local/persistent surrogate registry
    """

    zope.interface.implements(
        zope.app.registration.interfaces.IRegistry,
        )
    
    _surrogateClass = LocalSurrogate

    # Next local registry, may be None
    next = None

    subs = ()

    def __init__(self, base, next=None):

        # Base registry. This is always a global registry
        self.base = base

        self.adapters = {}
        self.stacks = PersistentDict()
        AdapterRegistry.__init__(self)
        self.setNext(next)

    def setNext(self, next, base=None):
        if base is not None:
            self.base = base
        if self.next is not None:
            self.next.removeSub(self)
        if next is not None:
            next.addSub(self)
        self.next = next
        self.adaptersChanged()

    def addSub(self, sub):
        self.subs += (sub, )

    def removeSub(self, sub):
        self.subs = tuple([s for s in self.subs if s is not sub])

    def __getstate__(self):
        state = Persistent.__getstate__(self).copy()
        
        for name in ('_default', '_null', 'adapter_hook',
                     'lookup', 'lookup1', 'queryAdapter', 'get',
                     'subscriptions', 'queryMultiAdapter', 'subscribers'
                     ):
            del state[name]
        return state

    def __setstate__(self, state):
        Persistent.__setstate__(self, state)
        AdapterRegistry.__init__(self)
    
    def baseFor(self, spec):
        return self.base.get(spec)

    def queryRegistrationsFor(self, registration, default=None):
        stacks = self.stacks.get(registration.required)
        if stacks:
            stack = stacks.get((False, registration.with, registration.name,
                                registration.provided))
            if stack is not None:
                return stack

        return default

    _stackType = NotifyingRegistrationStack

    def createRegistrationsFor(self, registration):
        stacks = self.stacks.get(registration.required)
        if stacks is None:
            stacks = PersistentDict()
            self.stacks[registration.required] = stacks

        key = (False, registration.with, registration.name,
               registration.provided)
        stack = stacks.get(key)
        if stack is None:
            stack = self._stackType(self)
            stacks[key] = stack

        return stack


    def _updateAdaptersFromLocalData(self, adapters):
        for required, stacks in self.stacks.iteritems():
            if required is None:
                required = Default
            radapters = adapters.get(required)
            if not radapters:
                radapters = {}
                adapters[required] = radapters

            for key, stack in stacks.iteritems():
                registration = stack.active()
                if registration is not None:

                    # Needs more thought:
                    # We have to remove the proxy because we're
                    # storing the value amd we can't store proxies.
                    # (Why can't we?)  we need to think more about
                    # why/if this is truly safe
                    
                    radapters[key] = removeSecurityProxy(registration.factory)

    def adaptersChanged(self, *args):

        adapters = {}
        if self.next is not None:
            for required, radapters in self.next.adapters.iteritems():
                adapters[required] = radapters.copy()
        
        self._updateAdaptersFromLocalData(adapters)

        if adapters != self.adapters:
            self.adapters = adapters

            # Throw away all of our surrogates, rather than dirtrying
            # them individually
            AdapterRegistry.__init__(self)

            for sub in self.subs:
                sub.adaptersChanged()

    notifyActivated = notifyDeactivated = adaptersChanged

    def baseChanged(self):
        """Someone changed the base service

        This should only happen during testing
        """
        AdapterRegistry.__init__(self)
        for sub in self.subs:
            sub.baseChanged()
                

    def registrations(self):
        for stacks in self.stacks.itervalues():
            for stack in stacks.itervalues():
                for info in stack.info():
                    yield info['registration']


class LocalAdapterBasedService(
    zope.app.container.contained.Contained,
    Persistent,
    ):
    """A service that uses local surrogate registries

    A local surrogate-based service needs to maintain connections
    between it's surrogate registries and those of containing ans
    sub-services.

    The service must implement a `setNext` method that will be called
    with the next local service, which may be ``None``, and the global
    service. This method will be called when a service is bound.
    
    """

    zope.interface.implements(
        zope.app.site.interfaces.IBindingAware,
        )

    def __updateNext(self, servicename):
        next = zope.app.component.localservice.getNextService(
            self, servicename)
        global_ = zapi.getGlobalServices().getService(servicename)
        if next == global_:
            next = None
        self.setNext(next, global_)
        
    def bound(self, servicename):
        self.__updateNext(servicename)
        
        # Now, we need to notify any sub-site services. This is
        # a bit complicated because our immediate subsites might not have
        # the same service. Sigh
        sm = zapi.getServices(self)
        self.__notifySubs(sm.subSites, servicename)

    def unbound(self, servicename):
        sm = zapi.getServices(self)
        self.__notifySubs(sm.subSites, servicename)

    def __notifySubs(self, subs, servicename):
        for sub in subs:
            s = sub.queryLocalService(servicename)
            if s is not None:
                s.__updateNext(servicename)
            else:
                self.__notifySubs(sub.subSites, servicename)

