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
"""Interfaces for objects supporting registration

$Id$
"""
import zope.component.interfaces
from zope.interface import Interface, Attribute, implements
from zope.schema import TextLine, Field, Choice
from zope.schema.interfaces import ITextLine, IField

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.annotation.interfaces import IAnnotatable
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.container.interfaces import IContainerNamesContainer
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.event.interfaces import IObjectEvent

UnregisteredStatus = _('Unregistered')
RegisteredStatus = _('Registered')
ActiveStatus = _('Active')


class IRegistrationEvent(IObjectEvent):
    """An event that involves a registration"""

class IRegistrationActivatedEvent(IRegistrationEvent):
    """This event is fired, when a component's registration is activated."""

class IRegistrationDeactivatedEvent(IRegistrationEvent):
    """This event is fired, when a component's registration is deactivated."""

class INoLocalServiceError(Interface):
    """No local service to register with.
    """

class NoLocalServiceError(Exception):
    """No local service to configure

    An attempt was made to register a registration for which there is
    no local service.
    """

    implements(INoLocalServiceError)

class IRegistration(Interface):
    """Registration object

    A registration object represents a specific registration
    decision, such as registering an adapter or defining a permission.

    In addition to the attributes or methods defined here,
    registration objects will include additional attributes
    identifying how they should be used. For example, a service
    registration will provide a service type. An adapter
    registration will specify a used-for interface and a provided
    interface.
    """

    serviceType = Attribute("service type that manages "
                            "this registration type")
    # A string; typically a class attribute

    status = Choice(
        title=_("Registration status"),
        values=(UnregisteredStatus, RegisteredStatus, ActiveStatus),
        default=UnregisteredStatus
        )

    # BBB Deprecated methods, since their functionality is better implemented
    # using event, which is done now. 12/05/2004
    # ----------------------------------------------------------------------
    def activated():
        """Method called when a registration is made active.
        """

    def deactivated():
        """Method called when a registration is made inactive.
        """
    # ----------------------------------------------------------------------

    def usageSummary():
        """Single-line usage summary.

        This should include the registration keys and the kind of
        registration. For example, a service registration will have a
        usage summary that indicates a registration for a service of
        some type.  (e.g. "View Service")

        """

    def implementationSummary():
        """Single-line implementation summary.

        This summarizes the implementation of the thing being
        registered. For example, for local-component registrations,
        this will include the component path. For a page registration,
        this might include a template path and a dotted class name.
        """

#############################################################################
# BBB: Kept for backward-compatibility. 12/05/2004
class IComponentPath(ITextLine):
    """A component path

    This is just the interface for the ComponentPath field below.  We'll use
    this as the basis for looking up an appropriate widget.
    """

class ComponentPath(TextLine):
    """A component path

    Values of the field are absolute unicode path strings that can be
    traversed to get an object.
    """
    implements(IComponentPath)
#############################################################################


class IComponent(IField):
    """A component path

    This is just the interface for the ComponentPath field below.  We'll use
    this as the basis for looking up an appropriate widget.
    """

class Component(Field):
    """A component path

    Values of the field are absolute unicode path strings that can be
    traversed to get an object.
    """
    implements(IComponent)



class IComponentRegistration(IRegistration):
    """Registration object that uses a component path and a permission."""

    permission = Choice(
        title=_("The permission needed to use the component"),
        vocabulary="Permissions",
        required=False,
        )

    component = Component(
        title=_("Registration Component"),
        description=_("The component the registration is for."),
        required=True)

    #########################################################################
    # BBB: Kept for backward-compatibility. 12/05/2004
    componentPath = ComponentPath(
        title=_("Component path"),
        description=_("The path to the component; this may be absolute, "
                      "or relative to the nearest site management folder"),
        required=True)

    
    def getComponent():
        """Return the component named in the registration.

        This is provided for backward compatibility; please use the
        `component` attribute instead.
        """
    #########################################################################


class IRegistrationStack(Interface):
    """A stack of registrations for a set of parameters

    A service will have a registry containing registry stacks
    for specific parameters.  For example, an adapter service will
    have a registry stack for each given used-for and provided
    interface.

    The registry stack works like a stack: the first element is
    active; when it is removed, the element after it is automatically
    activated.  An explicit None may be present (at most once) to
    signal that nothing is active.  To deactivate an element, it is
    moved to the end.
    """

    def register(registration):
        """Register the given registration without activating it.

        Do nothing if the registration is already registered.
        """

    def unregister(registration):
        """Unregister the given registration.

        Do nothing if the registration is not registered.

        Implies deactivate() if the registration is active.
        """

    def registered(registration):
        """Is the registration registered?

        Return a boolean indicating whether the registration has been
        registered.
        """

    def activate(registration):
        """Make the registration active.

        The activated() method is called on the registration.  If
        another registration was previously active, its deactivated()
        method is called first.

        If the argument is None, the currently active registration if
        any is disabled and no new registration is activated.

        Raises a ValueError if the given registration is not registered.
        """

    def deactivate(registration):
        """Make the registration inactive.

        If the registration is active, the deactivated() method is
        called on the registration.  If this reveals a registration
        that was previously active, that registration's activated()
        method is called.

        Raises a ValueError if the given registration is not registered.

        The call has no effect if the registration is registered but
        not active.
        """

    def active():
        """Return the active registration, if any.

        Otherwise, returns None.
        """

    def info():
        """Return a sequence of registration information.

        The sequence items are mapping objects with keys:

        active -- A boolean indicating whether the registration is
                  active.

        registration -- The registration object.
        """

    def __nonzero__(self):
        """The registry is true iff it has no registrations."""


class IRegistry(zope.component.interfaces.IRegistry):
    """A component that can be configured using a registration manager."""

    def registrations(localOnly=False):
        """Returns a list of all registrations.

        This method returns a complete list of Registration objects, which can
        be used for 'queryRegistrationFor()', for example. Usually this method
        will return registrations from all accessible registries of the same
        kind, but if 'localOnly' is set to true only registrations defined in
        this registry will be returned.
        """

    def queryRegistrationsFor(registration, default=None):
        """Return an IRegistrationStack for the registration.

        Data on the registration is used to decide which registry to
        return. For example, a service manager will use the
        registration name attribute to decide which registry
        to return.

        Typically, an object that implements this method will also
        implement a method named queryRegistrations, which takes
        arguments for each of the parameters needed to specify a set
        of registrations.

        The registry must be in the context of the registry.

        """

    def createRegistrationsFor(registration):
        """Create and return an IRegistrationStack for the registration.

        Data on the registration is used to decide which regsitry to
        create. For example, a service manager will use the
        registration name attribute to decide which regsitry
        to create.

        Typically, an object that implements this method will also
        implement a method named createRegistrations, which takes
        arguments for each of the parameters needed to specify a set
        of registrations.

        Calling createRegistrationsFor twice for the same registration
        returns the same registry.

        The registry must be in the context of the registry.

        """


class IOrderedContainer(Interface):
    """Containers whose items can be reorderd."""

    def moveTop(names):
        """Move the objects corresponding to the given names to the top.
        """

    def moveUp(names):
        """Move the objects corresponding to the given names up.
        """

    def moveBottom(names):
        """Move the objects corresponding to the given names to the bottom.
        """

    def moveDown(names):
        """Move the objects corresponding to the given names down.
        """

class IRegistrationManager(IContainerNamesContainer, IOrderedContainer):
    """Manage Registrations
    """

class IRegisterableContainer(IContainer):
    """Containers with registration managers

    These are site-management folders of one sort or another.

    The container allows clients to access the registration manager
    without knowing it's name.

    TODO: At this point, it doesn't really make sense for regsitration
    managers to be items.  It would probably be better to expose the
    registrations as a separate tab.

    The container prevents deletion of the last registration manager.

    The container may allow more than one registration manager. If it
    has more than one, the one returned from an unnamed access is
    undefined.
    TODO: The container should allow one and only one.

    The registration manager container *also* supports local-module
    lookup.

    """

    def getRegistrationManager():
        """Get a registration manager.

        Find a registration manager.  Clients can get the
        registration manager without knowing its name. Normally,
        folders have one registration manager. If there is more than
        one, this method will return one; which one is undefined.

        An error is raised if no registration manager can be found.
        """

    def findModule(name):
        """Find the module of the given name.

        If the module can be find in the folder or a parent folder
        (within the site manager), then return it, otherwise, delegate
        to the module service.

        This must return None when the module is not found.

        """

    def resolve(name):
        """Resolve a dotted object name.

        A dotted object name is a dotted module name and an object
        name within the module.

        TODO: We really should switch to using some other character than
        a dot for the delimiter between the module and the object
        name.

        """

    def __setitem__(name, object):
        """Add to object"""

class IRegisterable(IAnnotatable, IContained):
    """A marker interface."""
    
    __parent__ = Field(
        constraint = ContainerTypesConstraint(IRegisterableContainer))

IRegisterableContainer['__setitem__'].setTaggedValue(
    'precondition',
    ItemTypePrecondition(IRegisterable, IRegisterableContainer))
    

class IRegistered(Interface):
    """An object that can keep track of its configured uses.

    The object need not implement this functionality itself, but must at
    least support doing so via an adapter.
    """

    def addUsage(location):
        """Add a usage by location.

        The location is the physical path to the registration object that
        configures the usage.
        """
    def removeUsage(location):
        """Remove a usage by location.

        The location is the physical path to the registration object that
        configures the usage.
        """
    def usages():
        """Return a sequence of locations.

        A location is a physical path to a registration object that
        configures a usage.
        """

    def registrations():
        """Return a sequence of registration objects for this object."""

class IAttributeRegisterable(IAttributeAnnotatable, IRegisterable):
    """A marker interface."""

class INoRegistrationManagerError(Interface):
    """No registration manager error
    """

class NoRegistrationManagerError(Exception):
    """No registration manager

    There is no registration manager in a site-management folder, or
    an operation would result in no registration manager in a
    site-management folder.

    """
    implements(INoRegistrationManagerError)
