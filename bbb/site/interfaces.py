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
"""Interfaces for folders.

$Id$
"""
from zope.interface import Interface, Attribute
import zope.schema
from zope.component.interfaces import IServiceService
from zope.app.container.interfaces import IContainer
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.registration import interfaces as registration
from zope.app.i18n import ZopeMessageIDFactory as _


class ILocalService(registration.IRegisterable):
    """A local service isn't a local service if it doesn't implement this.

    The contract of a local service includes collaboration with
    services above it.  A local service should also implement
    IRegisterable (which implies that it is adaptable to
    IRegistered).  Implementing ILocalService implies this.
    """


class ISimpleService(ILocalService, registration.IAttributeRegisterable):
    """Most local services should implement this instead of ILocalService.

    It implies a specific way of implementing IRegisterable,
    by subclassing IAttributeRegisterable.
    """

class IComponentManager(Interface):

    def queryComponent(type=None, filter=None, all=0):
        """Return all components that match the given type and filter

        The objects are returned a sequence of mapping objects with keys:

        path -- The component path

        component -- The component

        all -- A flag indicating whether all component managers in
               this place should be queried, or just the local one.

        """


class IPossibleSite(Interface):
    """An object that could be a site
    """

    def setSiteManager(sm):
        """Sets the service manager for this object.
        """

    def getSiteManager():
        """Returns the service manager contained in this object.

        If there isn't a service manager, raise a component lookup.
        """

class ISite(IPossibleSite):
    """Marker interface to indicate that we have a site
    """

class IBindingAware(Interface):

    def bound(name):
        """Inform a service component that it is providing a service

        Called when an immediately-containing service manager binds
        this object to perform the named service.
        """

    def unbound(name):
        """Inform a service component that it is no longer providing a service

        Called when an immediately-containing service manager unbinds
        this object from performing the named service.
        """


class ISiteManager(IServiceService, IComponentManager,
                   registration.IRegistry):
    """Service Managers act as containers for Services.

    If a Service Manager is asked for a service, it checks for those it
    contains before using a context-based lookup to find another service
    manager to delegate to.  If no other service manager is found they defer
    to the ComponentArchitecture ServiceManager which contains file based
    services.
    """

    def queryRegistrations(name, default=None):
        """Return an IRegistrationRegistry for the registration name.

        queryRegistrationsFor(cfg, default) is equivalent to
        queryRegistrations(cfg.name, default)
        """

    def createRegistrationsFor(registration):
        """Create and return an IRegistrationRegistry for the registration
        name.

        createRegistrationsFor(cfg, default) is equivalent to
        createRegistrations(cfg.name, default)
        """

    def listRegistrationNames():
        """Return a list of all registered registration names.
        """

    def queryActiveComponent(name, default=None):
        """Finds the registration registry for a given name, checks if it has
        an active registration, and if so, returns its component.  Otherwise
        returns default.
        """

    def queryLocalService(service_type, default=None):
        """Return a local service, if there is one

        A local service is one configured in the local service manager.
        """

    def addSubsite(subsite):
        """Add a subsite of the site

        Local sites are connected in a tree. Each site knows about
        its containing sites and its subsites.
        """

    next = Attribute('The site that this site is a subsite of.')


class IServiceRegistration(registration.IComponentRegistration):
    """Service Registration

    Service registrations are dependent on the components that they
    configure. They register themselves as component dependents.

    The name of a service registration is used to determine the service
    type.
    """

    name = zope.schema.TextLine(
        title=_("Name"),
        description=_("The name that is registered"),
        readonly=True,
        # Don't allow empty or missing name:
        required=True,
        min_length=1,
        )


class ISiteManagementFolder(
    registration.IRegisterableContainer,
    IContainer,
    ):
    """Component and component registration containers."""

    __parent__ = zope.schema.Field(
        constraint = ContainerTypesConstraint(
            ISiteManager,
            registration.IRegisterableContainer,
            ),
        )

class ISiteManagementFolders(IContainer, IComponentManager):
    """A collection of ISiteManagementFolder objects.

    An ISiteManagementFolders object supports simple containment as
    well as package query and lookup.
    
    """
