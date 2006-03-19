##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Features that will go away in Zope 3.5.

$Id$
"""

from persistent import Persistent

import zope.event

from zope import interface, schema
import zope.component.interfaces
import zope.deprecation
import zope.app.component.interfaces.registration
import zope.schema.vocabulary
from zope.app.i18n import ZopeMessageFactory as _
import zope.app.container.interfaces
import zope.app.container.constraints
from zope.interface import implements
from zope.security.checker import InterfaceChecker, CheckerPublic
from zope.security.proxy import Proxy, removeSecurityProxy
from zope.app import zapi
from zope.app.component.interfaces import registration as interfaces
from zope.app.container.btree import BTreeContainer
from zope.app.container.contained import Contained
from zope.app.event import objectevent
from zope.app.traversing.interfaces import TraversalError
from zope.app.i18n import ZopeMessageFactory as _
import zope.app.component.registration


InactiveStatus = _('Inactive')
ActiveStatus = _('Active')

class IRegistration(interface.Interface):
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

    status = schema.Choice(
        title=_("Registration status"),
        vocabulary= zope.schema.vocabulary.SimpleVocabulary(
            (zope.schema.vocabulary.SimpleTerm(InactiveStatus,
                                               title=InactiveStatus),
             zope.schema.vocabulary.SimpleTerm(ActiveStatus,
                                               title=ActiveStatus))),
        default=ActiveStatus
        )


class IComponentRegistration(IRegistration):
    """Registration object that uses a component.

    An interface can optionally be specified that describes the interface the
    component provides for the registry.
    
    The interface will be used to produce a proxy for the component, if
    the permission is also specified.
    """
    component = zope.app.component.interfaces.registration.Component(
        title=_("Registration Component"),
        description=_("The component the registration is for."),
        required=True)

    interface = schema.Field(
        title=_("Component Interface"),
        description=_("The interface the component provides through this "
                      "registration."),
        required=False,
        default=None)

    permission = schema.Choice(
        title=_("The permission needed to use the component"),
        vocabulary="Permissions",
        required=False
        )


class IRegistry(zope.component.interfaces.IRegistry):
    """A component that can be configured using a registration manager."""

    def register(registration):
        """Register a component with the registry using a registration.

        Once the registration is added to the registry, it will be active. If
        the registration is already registered with the registry, this method
        will quietly return.
        """

    def unregister(registration):
        """Unregister a component from the registry.

        Unregistering a registration automatically makes the component
        inactive. If the registration is not registered, this method will
        quietly return.
        """

    def registered(registration):
        """Determine whether a registration is registered with the registry.

        The method will return a Boolean value.
        """


class ILocatedRegistry(IRegistry):
    """A registry that is located in a tree of registries.

    
    """
    next = interface.Attribute(
        "Set the next local registry in the tree. This attribute "
        "represents the parent of this registry node. If the "
        "value is `None`, then this registry represents the "
        "root of the tree")

    subs = interface.Attribute(
        "A collection of registries that describe the next level "
        "of the registry tree. They are the children of this "
        "registry node. This attribute should never be "
        "manipulated manually. Use `addSub()` and `removeSub()` "
        "instead.")

    base = interface.Attribute(
        "Outside of the local registry tree lies the global "
        "registry, which is known as the base to every local "
        "registry in the tree.")

    def addSub(sub):
        """Add a new sub-registry to the node.

        Important: This method should *not* be used manually. It is
        automatically called by `setNext()`. To add a new registry to the
        tree, use `sub.setNext(self, self.base)` instead!
        """

    def removeSub(sub):
        """Remove a sub-registry to the node.

        Important: This method should *not* be used manually. It is
        automatically called by `setNext()`. To remove a registry from the
        tree, use `sub.setNext(None)` instead!
        """

    def setNext(next, base=None):
        """Set the next/parent registry in the tree.

        This method should ensure that all relevant registies are updated
        correctly as well.
        """


class IRegistrationManager(
    zope.app.container.interfaces.IContainerNamesContainer,
    ):
    """Manage Registrations"""
    zope.app.container.constraints.contains(IRegistration)

    def addRegistration(registration):
        """Add a registration to the manager.

        The function will automatically choose a name as which the
        registration will be known. The name of the registration inside this
        manager is returned.
        """


class IRegistrationManagerContained(zope.app.container.interfaces.IContained):
    """Objects that can be contained by the registration manager should
    implement this interface."""
    zope.app.container.constraints.containers(IRegistrationManager)


class IRegisterableContainer(zope.app.container.interfaces.IContainer):
    """Containers with registration managers

    These are site-management folders of one sort or another.

    The container allows clients to access the registration manager
    without knowing it's name.

    The registration manager container *also* supports local-module
    lookup.
    """

    registrationManager = schema.Field(
        title=_("Registration Manager"),
        description=_("The registration manager keeps track of all component "
                    "registrations."))


class IRegisterable(zope.app.container.interfaces.IContained):
    """Mark a component as registerable.

    All registerable components need to implement this interface. 
    """
    #zope.app.container.constraints.containers(IRegisterableContainer)


class IRegisterableContainerContaining(
    zope.app.container.interfaces.IContainer,
    ):
    """A container that can only contain `IRegisterable`s and
    `IRegisterableContainer`s.

    This interface was designed to be always used together with the
    `IRegisterableContainer`.
    """
    zope.app.container.constraints.contains(
        IRegisterable, IRegisterableContainer)
    

class IRegistered(interface.Interface):
    """An object that can track down its registrations.

    The object need not implement this functionality itself, but must at
    least support doing so via an adapter.
    """

    def registrations():
        """Return a sequence of registration objects for this object."""

class ILocalAdapterRegistry(IRegistry, ILocatedRegistry):
    pass

class ILocalUtility(IRegisterable):
    """Local utility marker.

    A marker interface that indicates that a component can be used as
    a local utility.

    Utilities should usually also declare they implement
    IAttributeAnnotatable, so that the standard adapter to
    IRegistered can be used; otherwise, they must provide
    another way to be adaptable to IRegistered.
    """

class IAdapterRegistration(IComponentRegistration):
    """Local Adapter Registration for Local Adapter Registry

    The adapter registration is used to provide local adapters via the
    adapter registry. It is an extended component registration, whereby the
    component is the adapter factory in this case.
    """
    required = schema.Choice(
        title = _("For interface"),
        description = _("The interface of the objects being adapted"),
        vocabulary="Interfaces",
        readonly = True,
        required=False,
        default=None)

    with = schema.Tuple(
        title = _("With interfaces"),
        description = _("Additionally required interfaces"),
        readonly=True,
        value_type = zope.schema.Choice(vocabulary='Interfaces'),
        required=False,
        default=())

    provided = schema.Choice(
        title = _("Provided interface"),
        description = _("The interface provided"),
        vocabulary="Interfaces",
        readonly = True,
        required = True)

    name = schema.TextLine(
        title=_(u"Name"),
        readonly=False,
        required=True,
        default=u''
        )

    permission = schema.Choice(
        title=_("The permission required for use"),
        vocabulary="Permission Ids",
        readonly=False,
        required=False,
        )

    # TODO: for now until we figure out a way to specify the factory directly
    factoryName = schema.TextLine(
        title=_(u"Factory Name"),
        readonly=False,
        required=False,
        )

class IUtilityRegistration(IAdapterRegistration):
    """Utility registration object.

    Adapter registries are also used to to manage utilities, since utilities
    are adapters that are instantiated and have no required interfaces. Thus,
    utility registrations must fulfill all requirements of an adapter
    registration as well.
    """

    name = zope.schema.TextLine(
        title=_("Register As"),
        description=_("The name under which the utility will be known."),
        readonly=False,
        required=True,
        default=u''
        )

    provided = zope.schema.Choice(
        title=_("Provided interface"),
        description=_("The interface provided by the utility"),
        vocabulary="Utility Component Interfaces",
        readonly=True,
        required=True,
        )



class RegistrationStatusProperty(object):
    """A descriptor used to implement `IRegistration`'s `status` property."""
    def __get__(self, inst, klass):
        registration = inst
        if registration is None:
            return self

        registry = registration.getRegistry()
        if registry and registry.registered(registration):
            return interfaces.ActiveStatus

        return interfaces.InactiveStatus

    def __set__(self, inst, value):
        registration = inst
        registry = registration.getRegistry()
        if registry is None:
            raise ValueError('No registry found.')

        if value == interfaces.ActiveStatus:
            if not registry.registered(registration):
                registry.register(registration)
                zope.event.notify(
                    zope.app.component.registration.RegistrationActivatedEvent(
                        registration)
                    )

        elif value == interfaces.InactiveStatus:
            if registry.registered(registration):
                registry.unregister(registration)
                zope.event.notify(
                  zope.app.component.registration.RegistrationDeactivatedEvent(
                    registration)
                  )
        else:
            raise ValueError(value)


class SimpleRegistration(Persistent, Contained):
    """Registration objects that just contain registration data"""
    implements(interfaces.IRegistration,
               interfaces.IRegistrationManagerContained)

    # See interfaces.IRegistration
    status = RegistrationStatusProperty()

    def getRegistry(self):
        """See interfaces.IRegistration"""
        raise NotImplementedError(
              'This method must be implemented by each specific regstration.')




# Note that I could get rid of the base class below, but why bother.
# The thing that uses it is going away too.  I really have no way of
# knowing that there aren't still registrations that use the older
# data structures.  The better approach will be to just stop using
# registrations.

NULL_COMPONENT = object()

class BBBComponentRegistration(object):

    _BBB_componentPath = None

    def __init__(self, component, permission=None):
        # BBB: 12/05/2004
        if isinstance(component, (str, unicode)):
            self.componentPath = component
        else:
            # We always want to set the plain component. Untrusted code will
            # get back a proxied component anyways.
            self.component = removeSecurityProxy(component)
        if permission == 'zope.Public':
            permission = CheckerPublic
        self.permission = permission

    def getComponent(self):
        return self.__BBB_getComponent()
    getComponent = zope.deprecation.deprecated(getComponent,
                              'Use component directly. '
                              'The reference will be gone in Zope 3.3.')

    def __BBB_getComponent(self):
        if self._component is NULL_COMPONENT:
            return self.__BBB_old_getComponent(self._BBB_componentPath)

        # This condition should somehow make it in the final code, since it
        # honors the permission.
        if self.permission:
            checker = InterfaceChecker(self.getInterface(), self.permission)
            return Proxy(self._component, checker)

        return self._component

    def __BBB_old_getComponent(self, path):
        service_manager = zapi.getSiteManager(self)

        # Get the root and unproxy it
        if path.startswith("/"):
            # Absolute path
            root = removeAllProxies(zapi.getRoot(service_manager))
            component = zapi.traverse(root, path)
        else:
            # Relative path.
            ancestor = self.__parent__.__parent__
            component = zapi.traverse(ancestor, path)

        if self.permission:
            if type(component) is Proxy:
                # There should be at most one security Proxy around an object.
                # So, if we're going to add a new security proxy, we need to
                # remove any existing one.
                component = removeSecurityProxy(component)

            interface = self.getInterface()

            checker = InterfaceChecker(interface, self.permission)

            component = Proxy(component, checker)

        return component

    def __BBB_setComponent(self, component):
        self._BBB_componentPath = None
        self._component = component

    component = property(__BBB_getComponent, __BBB_setComponent)

    def __BBB_getComponentPath(self):
        if self._BBB_componentPath is not None:
            return self._BBB_componentPath
        return '/' + '/'.join(zapi.getPath(self.component))

    def __BBB_setComponentPath(self, path):
        self._component = NULL_COMPONENT
        self._BBB_componentPath = path

    componentPath = property(__BBB_getComponentPath, __BBB_setComponentPath)
    componentPath = zope.deprecation.deprecated(
        componentPath,
        'Use component directly. '
        'The reference will be gone in Zope 3.3.')

    def __setstate__(self, dict):
        super(BBBComponentRegistration, self).__setstate__(dict)
        # For some reason the component path is not set correctly by the
        # default __setstate__ mechanism.
        if 'componentPath' in dict:
            self._component = NULL_COMPONENT
            self._BBB_componentPath = dict['componentPath']

        if isinstance(self._BBB_componentPath, (str, unicode)):
            self._component = NULL_COMPONENT


class ComponentRegistration(BBBComponentRegistration,
                            SimpleRegistration):
    """Component registration.

    Subclasses should define a getInterface() method returning the interface
    of the component.
    """
    implements(interfaces.IComponentRegistration)

    def __init__(self, component, permission=None):
        super(ComponentRegistration, self).__init__(component, permission)
        if permission == 'zope.Public':
            permission = CheckerPublic
        self.permission = permission

    def _getComponent(self):
        if self.permission and self.interface:
            checker = InterfaceChecker(self.interface, self.permission)
            return Proxy(self._component, checker)
        return self._component

    def _setComponent(self, component):
        # We always want to set the plain component. Untrusted code will
        # get back a proxied component anyways.
        self._component = removeSecurityProxy(component)

    # See zope.app.component.interfaces.registration.IComponentRegistration
    component = property(_getComponent, _setComponent)

    # See zope.app.component.interfaces.registration.IComponentRegistration
    interface = None


class Registered:
    """An adapter from IRegisterable to IRegistered.

    This class is the only place that knows how 'Registered'
    data is represented.
    """
    implements(interfaces.IRegistered)
    __used_for__ = interfaces.IRegisterable

    def __init__(self, registerable):
        self.registerable = registerable

    def registrations(self):
        rm = zapi.getParent(self.registerable).registrationManager
        return [reg for reg in rm.values()
                if (interfaces.IComponentRegistration.providedBy(reg) and
                    reg.component is self.registerable)]


class RegistrationManager(BTreeContainer):
    """Registration manager

    Manages registrations within a package.
    """
    implements(interfaces.IRegistrationManager)

    @zope.deprecation.deprecate("Will go away in Zope 3.5")
    def addRegistration(self, reg):
        "See IWriteContainer"
        key = self._chooseName('', reg)
        self[key] = reg
        return key

    def _chooseName(self, name, reg):
        """Choose a name for the registration."""
        if not name:
            name = reg.__class__.__name__

        i = 1
        chosenName = name
        while chosenName in self:
            i += 1
            chosenName = name + str(i)

        return chosenName

class RegisterableContainer(object):
    """Mix-in to implement `IRegisterableContainer`"""

    def __init__(self):
        super(RegisterableContainer, self).__init__()
        self.__createRegistrationManager()

    def __createRegistrationManager(self):
        "Create a registration manager and store it as `registrationManager`"
        # See interfaces.IRegisterableContainer
        self.registrationManager = RegistrationManager()
        self.registrationManager.__parent__ = self
        self.registrationManager.__name__ = '++registrations++'
        zope.event.notify(
            objectevent.ObjectCreatedEvent(self.registrationManager))


class RegistrationManagerNamespace:
    """Used to traverse to a Registration Manager from a
       Registerable Container."""
    __used_for__ = interfaces.IRegisterableContainer

    def __init__(self, ob, request=None):
        self.context = ob.registrationManager

    def traverse(self, name, ignore):
        if name == '':
            return self.context
        raise TraversalError(self.context, name)



class AdapterRegistration(ComponentRegistration):
    """Adapter component registration for persistent components

    This registration configures persistent components in packages to
    be adapters.
    """
    zope.interface.implements(IAdapterRegistration)

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
        factory = resolve(self.factoryName, self)
        return factory
    component = property(component)

    def getRegistry(self):
        return zapi.getSiteManager(self)

