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
import zodbcode.module

import zope.event
import zope.interface
import zope.component
from zope.component.exceptions import ComponentLookupError

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
from zope.app.filerepresentation.interfaces import IDirectoryFactory
from zope.app.traversing.interfaces import IContainmentRoot


class SiteManagementFolder(registration.RegisterableContainer,
                           BTreeContainer):
    zope.interface.implements(interfaces.ISiteManagementFolder)


class SMFolderFactory(object):
    zope.interface.implements(IDirectoryFactory)

    def __init__(self, context):
        self.context = context

    def __call__(self, name):
        return SiteManagementFolder()


class SiteManagerContainer(Contained):
    """Implement access to the service manager (++etc++site).

    This is a mix-in that implements the IPossibleSite
    interface; for example, it is used by the Folder implementation.
    """
    zope.interface.implements(interfaces.IPossibleSite)

    __sm = None

    def getSiteManager(self):
        if self.__sm is not None:
            return self.__sm
        else:
            raise ComponentLookupError('no site manager defined')

    def setSiteManager(self, sm):
        if interfaces.ISite.providedBy(self):
            raise TypeError("Already a site")

        if zope.component.interfaces.ISiteManager.providedBy(sm):
            self.__sm = sm
            sm.__name__ = '++etc++site'
            sm.__parent__ = self
        else:
            raise ValueError('setSiteManager requires an ISiteManager')

        zope.interface.directlyProvides(
            self, interfaces.ISite,
            zope.interface.directlyProvidedBy(self))


def findNextSiteManager(site):
    next = None
    while next is None:
        if IContainmentRoot.providedBy(site):
            # we're the root site, use the global sm
            next = zapi.getGlobalSiteManager()

        site = zapi.getParent(site)

        if interfaces.ISite.providedBy(site):
            next = site.getSiteManager()

    return next
    

class LocalSiteManager(BTreeContainer,
                       zodbcode.module.PersistentModuleRegistry,
                       zope.component.site.SiteManager):
    """Local Site Manager implementation"""
    zope.interface.implements(
        interfaces.ILocalSiteManager,
        interfaces.registration.IRegisterableContainerContaining)

    # See interfaces.registration.ILocatedRegistry
    next = None
    subs = ()
    base = None

    def __init__(self, site):
        # Locate the site manager
        self.__parent__ = site
        self.__name__ = '++etc++site'

        # Make sure everything is setup correctly
        BTreeContainer.__init__(self)
        zodbcode.module.PersistentModuleRegistry.__init__(self)

        # Setup located registry attributes
        self.base = zapi.getGlobalSiteManager()
        next = findNextSiteManager(site)
        if not zope.component.site.IGlobalSiteManager.providedBy(next):
            self.setNext(next)

        # Set up adapter registries
        gsm = zapi.getGlobalSiteManager()
        self.adapters = adapter.LocalAdapterRegistry(gsm.adapters)
        self.utilities = adapter.LocalAdapterRegistry(gsm.utilities)

        # Setup default site management folder
        folder = SiteManagementFolder()
        zope.event.notify(objectevent.ObjectCreatedEvent(folder))
        self['default'] = folder


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
        if self.next is not None:
            self.next.removeSub(self)
        if next is not None:
            next.addSub(self)
        self.next = next
        self.adapaters.setNext(next.adapters)
        self.utilities.setNext(next.adapters)

    def __getRegistry(registration):
        """Determine the correct registry for the registration."""
        if interfaces.IUtilityRegistration.providedBy(registration):
            return self.utilities
        elif interfaces.IAdapterRegistration.providedBy(registration):
            return self.adapters
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
    # Make the adapter code happy.
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
from zope.testing.cleanup import addCleanUp
addCleanUp(clearSite)


def SiteManagerAdapter(ob):
    """An adapter from ILocation to ISiteManager.

    The ILocation is interpreted flexibly, we just check for
    ``__parent__``.
    """
    current = ob
    while True:
        if interfaces.ISite.providedBy(current):
            return current.getSiteManager()
        current = getattr(current, '__parent__', None)
        if current is None:
            raise ComponentLookupError(
                "Could not adapt %r to ISiteManager" %ob)


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
