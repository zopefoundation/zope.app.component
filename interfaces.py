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
"""Interfaces for the Local Component Architecture

$Id$
"""
import zope.interface
import zope.schema
from zope.component.interfaces import ISiteManager
from zope.app.container.interfaces import IContainer
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.registration import interfaces as registration


class IComponentManager(zope.interface.Interface):

    def queryComponent(type=None, filter=None, all=0):
        """Return all components that match the given type and filter

        The objects are returned a sequence of mapping objects with keys:

        path -- The component path

        component -- The component

        all -- A flag indicating whether all component managers in
               this place should be queried, or just the local one.
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

class IPossibleSite(zope.interface.Interface):
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

class ILocalSiteManager(ISiteManager, IComponentManager,
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


class ISiteManagementFolder(registration.IRegisterableContainer,
                            IContainer):
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

class ILocalUtility(registration.IRegisterable):
    """Local utility marker.

    A marker interface that indicates that a component can be used as
    a local utility.

    Utilities should usually also declare they implement
    IAttributeAnnotatable, so that the standard adapter to
    IRegistered can be used; otherwise, they must provide
    another way to be adaptable to IRegistered.
    """


class IAdapterRegistration(registration.IRegistration):

    required = zope.schema.Choice(
        title = _(u"For interface"),
        description = _(u"The interface of the objects being adapted"),
        vocabulary="Interfaces",
        readonly = True)

    provided = zope.schema.Choice(
        title = _(u"Provided interface"),
        description = _(u"The interface provided"),
        vocabulary="Interfaces",
        readonly = True,
        required = True)

    name = zope.schema.TextLine(
        title=_(u"Name"),
        readonly=True,
        required=False,
        )

    factoryName = zope.schema.BytesLine(
        title=_(u"The dotted name of a factory for creating the adapter"),
        readonly = True,
        required = True,
        )

    permission = zope.schema.Choice(
        title=_(u"The permission required for use"),
        vocabulary="Permission Ids",
        readonly=False,
        required=False,
        )
        
    factory = zope.interface.Attribute(
        _("Factory to be called to construct the component")
        )

class IUtilityRegistration(registration.IComponentRegistration):
    """Utility registration object.

    This is keyed off name (which may be empty) and interface. It inherits the
    `component` property.
    """

    name = zope.schema.TextLine(
        title=_("Register As"),
        description=_("The name that is registered"),
        readonly=True,
        required=True,
        )

    interface = zope.schema.Choice(
        title=_("Provided interface"),
        description=_("The interface provided by the utility"),
        vocabulary="Utility Component Interfaces",
        readonly=True,
        required=True,
        )
