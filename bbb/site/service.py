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
"""Service manager implementation

A service manager has a number of roles:

  - A service service

  - A place to do TTW development or to manage database-based code

  - A registry for persistent modules.  The Zope import hook uses the
    ServiceManager to search for modules.  (This functionality will
    eventually be replaced by a separate module service.)

$Id$
"""
import sys
from transaction import get_transaction
from zodbcode.module import PersistentModuleRegistry

import zope.event
import zope.interface
from zope.component.exceptions import ComponentLookupError

import zope.app.registration.interfaces
from zope.app import zapi
from zope.app.component.localservice import getNextService
from zope.app.component.localservice import getNextServices
from zope.app.container.btree import BTreeContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.contained import Contained
from zope.app.container.interfaces import IContainer
from zope.app.event import objectevent
from zope.app.registration.interfaces import IRegistry
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.traversing.api import getPath
from zope.app.location import inside
from zope.app.site.folder import SiteManagementFolder
from zope.app.registration.registration import ComponentRegistration
from zope.app.registration.registration import RegistrationStack

from zope.app.site.interfaces import IBindingAware, ILocalService
from zope.app.site.interfaces import IPossibleSite, ISite, ISiteManager
from zope.app.site.interfaces import IServiceRegistration

class IRegisterableContainerContainer(zope.interface.Interface):

    def __setitem__(name, folder):
        """Add a site-management folder
        """
    __setitem__.precondition = ItemTypePrecondition(
       zope.app.registration.interfaces.IRegisterableContainer)


class SiteManager(BTreeContainer, PersistentModuleRegistry):

    zope.interface.implements(ISiteManager,
                              IRegisterableContainerContainer,
                              IRegistry)

    def __init__(self, site):
        self._bindings = {}
        self.__parent__ = site
        self.__name__ = '++etc++site'
        BTreeContainer.__init__(self)
        PersistentModuleRegistry.__init__(self)
        self.subSites = ()
        self._setNext(site)
        folder = SiteManagementFolder()
        zope.event.notify(objectevent.ObjectCreatedEvent(folder))
        self['default'] = folder

    def _setNext(self, site):
        """Find set the next service manager
        """
        while True:
            if IContainmentRoot.providedBy(site):
                # we're the root site, use the global sm
                self.next = zapi.getGlobalServices()
                return
            site = site.__parent__
            if site is None:
                raise TypeError("Not enough context information")
            if ISite.providedBy(site):
                self.next = site.getSiteManager()
                self.next.addSubsite(self)
                return

    def addSubsite(self, sub):
        """See ISiteManager interface
        """
        subsite = sub.__parent__

        # Update any sites that are now in the subsite:
        subsites = []
        for s in self.subSites:
            if inside(s, subsite):
                s.next = sub
                sub.addSubsite(s)
            else:
                subsites.append(s)

        subsites.append(sub)
        self.subSites = tuple(subsites)

    def queryRegistrationsFor(self, cfg, default=None):
        """See IRegistry"""
        return self.queryRegistrations(cfg.name, default)

    def queryRegistrations(self, name, default=None):
        """See INameRegistry"""
        return self._bindings.get(name, default)

    def createRegistrationsFor(self, cfg):
        """See IRegistry"""
        return self.createRegistrations(cfg.name)

    def createRegistrations(self, name):
        try:
            registry = self._bindings[name]
        except KeyError:
            registry = RegistrationStack(self)
            self._bindings[name] = registry
            self._p_changed = 1
        return registry

    def listRegistrationNames(self):
        return filter(self._bindings.get,
                      self._bindings.keys())

    def queryActiveComponent(self, name, default=None):
        registry = self.queryRegistrations(name)
        if registry:
            registration = registry.active()
            if registration is not None:
                return registration.component
        return default

    def getServiceDefinitions(self):
        """See IServiceService
        """
        # Get the services defined here and above us, if any (as held
        # in a ServiceInterfaceService, presumably)
        sm = self.next
        if sm is not None:
            serviceDefs = sm.getServiceDefinitions()
        else:
            serviceDefs = {}

        return serviceDefs

    def getService(self, name):
        """See IServiceService
        """

        # This is rather tricky. Normally, getting a service requires
        # the use of other services, like the adapter service.  We
        # need to be careful not to get into an infinite recursion by
        # getting out getService to be called while looking up
        # services, so we'll use _v_calling to prevent recursive
        # getService calls.

        if name == 'Services':
            return self # We are the service service

        if not getattr(self, '_v_calling', False):

            self._v_calling = True
            try:
                service = self.queryActiveComponent(name)
                if service is not None:
                    return service
            finally:
                self._v_calling = False

        return getNextService(self, name)

    def queryLocalService(self, name, default=None):
        """See ISiteManager
        """

        # This is rather tricky. Normally, getting a service requires
        # the use of other services, like the adapter service.  We
        # need to be careful not to get into an infinate recursion by
        # getting our getService to be called while looking up
        # services, so we'll use _v_calling to prevent recursive
        # getService calls.

        if name == 'Services':
            return self # We are the service service

        if not getattr(self, '_v_calling', False):

            self._v_calling = True
            try:
                service = self.queryActiveComponent(name)
                if service is not None:
                    return service
            finally:
                self._v_calling = False

        return default

    def getInterfaceFor(self, service_type):
        """See IServiceService
        """
        for type, interface in self.getServiceDefinitions():
            if type == service_type:
                return interface

        raise NameError(service_type)

    def queryComponent(self, type=None, filter=None, all=0):
        local = []
        path = getPath(self)
        for pkg_name in self:
            package = self[pkg_name]
            for name in package:
                component = package[name]
                if type is not None and not type.providedBy(component):
                    continue
                if filter is not None and not filter(component):
                    continue
                local.append({'path': "%s/%s/%s" % (path, pkg_name, name),
                              'component': component,
                              })

        if all:
            next_service_manager = self.next
            if IComponentManager.providedBy(next_service_manager):
                next_service_manager.queryComponent(type, filter, all)

            local += list(all)

        return local

    def findModule(self, name):
        # override to pass call up to next service manager
        mod = super(ServiceManager, self).findModule(name)
        if mod is not None:
            return mod

        sm = self.next
        try:
            findModule = sm.findModule
        except AttributeError:
            # The only service manager that doesn't implement this
            # interface is the global service manager.  There is no
            # direct way to ask if sm is the global service manager.
            return None
        return findModule(name)

    def __import(self, module_name):
        mod = self.findModule(module_name)
        if mod is None:
            mod = sys.modules.get(module_name)
            if mod is None:
                raise ImportError(module_name)

        return mod

ServiceManager = SiteManager # Backward compat

class ServiceRegistration(ComponentRegistration):
    """Registrations for named components.

    This configures components that live in folders, by name.
    """

    serviceType = zapi.servicenames.Services

    zope.interface.implements(IServiceRegistration)

    def __init__(self, name, service, context=None):
        super(ServiceRegistration, self).__init__(service, None)
        self.name = name

        if context is not None:
            # Check that the object implements stuff we need
            self.__parent__ = context
            if not ILocalService.providedBy(service):
                raise TypeError(
                    "service %r doesn't implement ILocalService" %
                    service)
        # Else, this must be a hopeful test invocation

    def getInterface(self):
        service_manager = zapi.getServices(self)
        return service_manager.getInterfaceFor(self.name)

    def usageSummary(self):
        return self.name + " Service"


def handleActivated(event):
    if isinstance(event.object, ServiceRegistration):
        service = event.object.component
        if IBindingAware.providedBy(service):
            service.bound(event.object.name)

def handleDeactivated(event):
    if isinstance(event.object, ServiceRegistration):
        service = event.object.component
        if IBindingAware.providedBy(service):
            service.unbound(event.object.name)
