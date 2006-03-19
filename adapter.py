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
"""DEPRECATED"""

import warnings

warnings.warn(
    "This module is deprecated and will go away in Zope 3.5",
    DeprecationWarning, 2)


import persistent

import zope.interface
from zope.security.proxy import removeSecurityProxy

from zope.app.component import registration
from zope.app.component import interfaces
from zope.app import zapi


class LocalAdapterRegistry(zope.interface.adapter.AdapterRegistry,
                           persistent.Persistent):
    """Local/persistent surrogate registry"""
    zope.interface.implements(interfaces.ILocalAdapterRegistry)

    # See interfaces.registration.ILocatedRegistry
    next = None
    subs = ()

    def __init__(self, base, next=None):
        # Base registry. This is always a global registry
        self.base = base
        # `adapters` is simple dict, since it is populated during every load
        self.adapters = {}
        self._registrations = ()
        super(LocalAdapterRegistry, self).__init__()
        self.setNext(next)

    def addSub(self, sub):
        """See interfaces.registration.ILocatedRegistry"""
        self.subs += (sub, )

    def removeSub(self, sub):
        """See interfaces.registration.ILocatedRegistry"""
        self.subs = tuple(
            [s for s in self.subs if s is not sub] )

    def setNext(self, next, base=None):
        """See interfaces.registration.ILocatedRegistry"""
        if base is not None:
            self.base = base

        if next != self.next:
            if self.next is not None:
                self.next.removeSub(self)
            if next is not None:
                next.addSub(self)
            self.next = next

        self.__bases__ = tuple([b for b in (next, self.base) if b is not None])

        for sub in self.subs:
            sub.setNext(self)
            

    def register(self, registration):
        """See zope.app.component.interfaces.registration.IRegistry"""
        self._registrations += (registration,)

        zope.interface.adapter.AdapterRegistry.register(
            self,
            (registration.required, ) + registration.with,
            registration.provided, registration.name,
            registration.component,
            )

    def unregister(self, registration):
        """See zope.app.component.interfaces.registration.IRegistry"""
        self._registrations = tuple([reg for reg in self._registrations
                                     if reg is not registration])

        zope.interface.adapter.AdapterRegistry.unregister(
            self,
            (registration.required, ) + registration.with,
            registration.provided, registration.name,
            registration.component,
            )

    def registered(self, registration):
        """See zope.app.component.interfaces.registration.IRegistry"""
        return registration in self._registrations

    def registrations(self):
        """See zope.app.component.interfaces.registration.IRegistry"""
        return self._registrations

class AdapterRegistration(registration.ComponentRegistration):
    """A simple implementation of the adapter registration interface."""
    zope.interface.implements(interfaces.IAdapterRegistration)

    def __init__(self, required, provided, factory,
                 name='', permission=None, registry=None):
        if not isinstance(required, (tuple, list)):
            self.required = required
            self.with = ()
        else:
            self.required = required[0]
            self.with = tuple(required[1:])
        self.provided = provided
        self.name = name
        self.component = factory
        self.permission = permission
        self.registry = registry

    def getRegistry(self):
        return self.registry

    def __repr__(self):
        return ('<%s: ' %self.__class__.__name__ +
                'required=%r, ' %self.required +
                'with=' + `self.with` + ', ' +
                'provided=%r, ' %self.provided +
                'name=%r, ' %self.name +
                'component=%r, ' %self.component +
                'permission=%r' %self.permission +
                '>')

class LocalUtilityRegistry(LocalAdapterRegistry):

    zope.deprecation.deprecate(
        "Will go away in Zope 3.5.  Use registerUtility instead."
        )
    def register(self, registration):
        """See zope.app.component.interfaces.registration.IRegistry"""
        self._registrations += (registration,)

        zope.interface.adapter.AdapterRegistry.register(
            self,
            (),
            registration.provided, registration.name,
            registration.component,
            )

        # XXX need test that this second part happens
        zope.interface.adapter.AdapterRegistry.subscribe(
            self,
            (),
            registration.provided,
            registration.component,
            )

    zope.deprecation.deprecate(
        "Will go away in Zope 3.5.  Use unregisterUtility instead."
        )
    def unregister(self, registration):
        """See zope.app.component.interfaces.registration.IRegistry"""
        self._registrations = tuple([reg for reg in self._registrations
                                     if reg is not registration])

        zope.interface.adapter.AdapterRegistry.unregister(
            self,
            (),
            registration.provided, registration.name,
            registration.component,
            )


        # XXX need test that this second part happens
        zope.interface.adapter.AdapterRegistry.unsubscribe(
            self,
            (),
            registration.provided,
            registration.component,
            )

    zope.deprecation.deprecate(
        "Will go away in Zope 3.5.  "
        "Use registeredUtilities on site manager instead."
        )
    @zope.deprecation.deprecate("Will go away in Zope 3.5")
    def registered(self, registration):
        raise TypeError("We never supported adapters")

    @zope.deprecation.deprecate("Will go away in Zope 3.5")
    def registrations(self):
        raise TypeError("We never supported adapters")


class UtilityRegistration(registration.ComponentRegistration):
    """Utility component registration for persistent components

    This registration configures persistent components in packages to
    be utilities.
    """
    zope.interface.implements(interfaces.IUtilityRegistration)

    def __init__(self, name, provided, component, permission=None):
        super(UtilityRegistration, self).__init__(component, permission)
        self.name = name
        self.provided = provided

    def getRegistry(self):
        return zapi.getSiteManager(self)
