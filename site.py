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
"""Site and Local Site Manager implementation

A local manager has a number of roles:

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
from zope.app.component.hooks import setSite
from zope.app.container.btree import BTreeContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.contained import Contained
from zope.app.container.interfaces import IContainer
from zope.app.event import objectevent
from zope.app.location import inside
from zope.app.registration.interfaces import IRegistry
from zope.app.registration.registration import ComponentRegistration
from zope.app.registration.registration import RegistrationStack
from zope.app.site.folder import SiteManagementFolder
from zope.app.traversing.interfaces import IContainmentRoot

from zope.app.site.interfaces import IPossibleSite, ISite, ISiteManager

class IRegisterableContainerContainer(zope.interface.Interface):

    def __setitem__(name, folder):
        """Add a site-management folder
        """
    __setitem__.precondition = ItemTypePrecondition(
       zope.app.registration.interfaces.IRegisterableContainer)


class LocalSiteManager(BTreeContainer, PersistentModuleRegistry):

    zope.interface.implements(ILocalSiteManager,
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


    def queryComponent(self, type=None, filter=None, all=0):
        local = []
        path = zapi.getPath(self)
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


class AdapterRegistration(
    zope.app.registration.registration.SimpleRegistration):

    zope.interface.implements(IAdapterRegistration)

    serviceType = zapi.servicenames.Adapters

    with = () # Don't support multi-adapters yet

    # TODO: These should be positional arguments, except that required
    #       isn't passed in if it is omitted. To fix this, we need a
    #       required=False,explicitly_unrequired=True in the schema field
    #       so None will get passed in.
    def __init__(self, provided, factoryName,
                 name='', required=None, permission=None):
        self.required = required
        self.provided = provided
        self.name = name
        self.factoryName = factoryName
        self.permission = permission

    def factory(self):
        folder = self.__parent__.__parent__
        factory = folder.resolve(self.factoryName)
        return factory
    factory = property(factory)



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


def threadSiteSubscriber(event):
    """A subscriber to BeforeTraverseEvent

    Sets the 'site' thread global if the object traversed is a site.
    """
    if ISite.providedBy(event.object):
        setSite(event.object)


def clearThreadSiteSubscriber(event):
    """A subscriber to EndRequestEvent

    Cleans up the site thread global after the request is processed.
    """
    clearSite()

# Clear the site thread global
clearSite = setSite
