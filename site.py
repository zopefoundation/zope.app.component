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

A local site manager has a number of roles:

  - A local site manager, that provides a local adapter and utility registry. 

  - A place to do TTW development and/or to manage database-based code.

  - A registry for persistent modules.  The Zope 3 import hook uses the
    SiteManager to search for modules.

$Id$
"""
import sys
from zodbcode.module import PersistentModuleRegistry

import zope.event
import zope.interface
from zope.component.exceptions import ComponentLookupError
from zope.component.site import SiteManager

from zope.app import zapi
from zope.app.component import adapter
from zope.app.component import interfaces
from zope.app.component import registration
from zope.app.component.hooks import setSite
from zope.app.container.btree import BTreeContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.contained import Contained
from zope.app.container.interfaces import IContainer
from zope.app.event import objectevent
from zope.app.location import inside
from zope.app.traversing.interfaces import IContainmentRoot


class SiteManagementFolder(RegisterableContainer, BTreeContainer):
    implements(interfaces.ISiteManagementFolder)

class SMFolderFactory(object):
    implements(IDirectoryFactory)

    def __init__(self, context):
        self.context = context

    def __call__(self, name):
        return SiteManagementFolder()


class LocalSiteManager(BTreeContainer, PersistentModuleRegistry, SiteManager):
    """Local Site Manager implementation"""
    zope.interface.implements(
        interfaces.ILocalSiteManager,
        interfaces.registrations.IRegisterableContainerContainer)

    def __init__(self, site):
        # Locate the site manager
        self.__parent__ = site
        self.__name__ = '++etc++site'
        # Make sure everything is setup correctly
        BTreeContainer.__init__(self)
        PersistentModuleRegistry.__init__(self)
        # Set up adapter registries
        self.adapters = adapter.LocalAdapterRegistry()
        self.utilities = adapter.LocalAdapterRegistry()
        # Initialize all links
        self.subSites = ()
        self._setNext(site)
        # Setup default site management folder
        folder = SiteManagementFolder()
        zope.event.notify(objectevent.ObjectCreatedEvent(folder))
        self['default'] = folder

    def _setNext(self, site):
        """Find and set the next site manager"""
        next = None
        while next is None:
            if IContainmentRoot.providedBy(site):
                # we're the root site, use the global sm
                next = zapi.getGlobalServices()

            site = zapi.getParent(site)

            if ISite.providedBy(site):
                next = site.getSiteManager()
                next.addSubsite(self)
                return

        self.next = next
        self.adapters.setNextRegistry(next.adapters)
        self.utilities.setNextRegistry(next.utilities)


    def addSubsite(self, sub):
        """See ILocalSiteManager interface"""
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
        self.adapters.addSubRegistry(sub.adapters)
        self.utilities.addSubRegistry(sub.utilities)

    def __getRegistry(registration):
        """Determine the correct registry for the registration."""
        if IAdapterRegistration.providedBy(registration):
            return self.adapters
        elif IUtilityRegistration.providedBy(registration):
            return self.utilities
        raise ValueError, \
              ("Unable to detect registration type or registration "
               "type is not supported. The registration object must provide "
               "`IAdapterRegistration` or `IUtilityRegistration`.")

    def register(self, registration):
        """See zope.app.component.interfaces.registration.IRegistry"""
        registry = self.__getRegistry()
        registry.register(registration)

    def unregister(self, registration):
        """See zope.app.component.interfaces.registration.IRegistry"""
        registry = self.__getRegistry()
        registry.unregister(registration)        

    def registered(self, registration):
        """See zope.app.component.interfaces.registration.IRegistry"""
        return self.adapters.registered(registration) or \
               self.utilities.registered(registration)

    def registrations(self):
        """See zope.component.interfaces.IRegistry"""
        for reg in self.adapters.registrations():
            yield reg
        for reg in self.utilities.registrations():
            yield reg

    def queryComponent(self, type=None, filter=None, all=True):
        """See zope.app.component.interfaces.IComponentManager"""
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
                local.append({'path': "%s/%s/%s" %(path, pkg_name, name),
                              'component': component,
                              })

        if all:
            next_service_manager = self.next
            if IComponentManager.providedBy(next_service_manager):
                next_service_manager.queryComponent(type, filter, all)

            local += list(all)

        return local

    def findModule(self, name):
        """See zodbcode.interfaces.IPersistentModuleImportRegistry"""
        # override to pass call up to next service manager
        mod = super(SiteManager, self).findModule(name)
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


    def __import(self, name):
        # Look for a .py file first:
        manager = self.get(name+'.py')
        if manager is not None:
            # found an item with that name, make sure it's a module(manager):
            if IModuleManager.providedBy(manager):
                return manager.getModule()

        # Look for the module in this folder:
        manager = self.get(name)
        if manager is not None:
            # found an item with that name, make sure it's a module(manager):
            if IModuleManager.providedBy(manager):
                return manager.getModule()

        raise ImportError(name)


    def resolve(self, name):
        l = name.rfind('.')
        mod = self.findModule(name[:l])
        return getattr(mod, name[l+1:])


class AdapterRegistration(registration.ComponentRegistration):
    """Adapter component registration for persistent components

    This registration configures persistent components in packages to
    be adapters.
    """
    zope.interface.implements(interfaces.IAdapterRegistration)

    def __init__(self, required, provided, factoryName,
                 name='', permission=None):
        if not isinstance(required, (tuple, list)):
            self.required = required
            self.with = ()
        else:
            self.required = required[0]
            self.with = tuple(required[1:])
        self.provided = provided
        self.name = name
        self.factoryName = factoryName
        self.permission = permission

    def component(self):
        folder = self.__parent__.__parent__
        factory = folder.resolve(self.factoryName)
        return factory
    component = property(component)

    def getRegistry(self):
        return zapi.getSiteManager(self)


class UtilityRegistration(registration.ComponentRegistration):
    """Utility component registration for persistent components

    This registration configures persistent components in packages to
    be utilities.
    """
    zope.interface.implements(interfaces.IUtilityRegistration)

    ############################################################
    # To make adapter code happy. Are we going too far?
    required = zope.interface.adapter.Null
    with = ()
    ############################################################

    def __init__(self, name, provided, component, permission=None):
        super(UtilityRegistration, self).__init__(component, permission)
        self.name = name
        self.provided = provided

    def getRegistry(self):
        return self.getSiteManager()


def threadSiteSubscriber(event):
    """A subscriber to BeforeTraverseEvent

    Sets the 'site' thread global if the object traversed is a site.
    """
    if interfaces.ISite.providedBy(event.object):
        setSite(event.object)


def clearThreadSiteSubscriber(event):
    """A subscriber to EndRequestEvent

    Cleans up the site thread global after the request is processed.
    """
    clearSite()

# Clear the site thread global
clearSite = setSite
