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
"""Component registration support for services

$Id$
"""
import sys
import warnings
from persistent import Persistent

import zope.cachedescriptors.property
import zope.event
from zope.interface import implements
from zope.exceptions import DuplicationError
from zope.proxy import removeAllProxies, getProxiedObject
from zope.security.checker import InterfaceChecker, CheckerPublic
from zope.security.proxy import Proxy, removeSecurityProxy

from zope.app import zapi
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.component.localservice import getLocalServices
from zope.app.container.contained import Contained
from zope.app.container.contained import setitem, contained, uncontained
from zope.app.copypastemove import ObjectCopier
from zope.app.dependable.interfaces import IDependable, DependencyError
from zope.app.event import objectevent
from zope.app.location import inside
from zope.app.module.interfaces import IModuleManager
from zope.app.registration import interfaces


class RegistrationEvent(objectevent.ObjectEvent):
    implements(interfaces.IRegistrationEvent)

class RegistrationActivatedEvent(RegistrationEvent):
    implements(interfaces.IRegistrationActivatedEvent)

class RegistrationDeactivatedEvent(RegistrationEvent):
    implements(interfaces.IRegistrationDeactivatedEvent)


class RegistrationStatusProperty(object):

    def __get__(self, inst, klass):
        if inst is None:
            return self

        registration = inst
        service = self._get_service(registration)
        registry = service and service.queryRegistrationsFor(registration)

        if registry:

            if registry.active() == registration:
                return interfaces.ActiveStatus
            if registry.registered(registration):
                return interfaces.RegisteredStatus

        return interfaces.UnregisteredStatus

    def __set__(self, inst, value):
        registration = inst
        service = self._get_service(registration)
        registry = service and service.queryRegistrationsFor(registration)

        if value == interfaces.UnregisteredStatus:
            if registry:
                registry.unregister(registration)

        else:
            if not service:
                raise interfaces.NoLocalServiceError(
                    "This registration change cannot be performed because "
                    "there isn't a corresponding %s service defined in this "
                    "site. To proceed, first add a local %s service."
                    % (registration.serviceType, registration.serviceType))

            if registry is None:
                registry = service.createRegistrationsFor(registration)

            if value == interfaces.RegisteredStatus:
                if registry.active() == registration:
                    registry.deactivate(registration)
                else:
                    registry.register(registration)

            elif value == interfaces.ActiveStatus:
                if not registry.registered(registration):
                    registry.register(registration)
                registry.activate(registration)

    def _get_service(self, registration):
        # how we get the service is factored out so subclasses can
        # approach this differently
        sm = zapi.getServices(registration)
        return sm.queryLocalService(registration.serviceType)


class RegistrationStack(Persistent, Contained):
    """Registration registry implemention

       A registration stack provides support for a collection of
       registrations such that, at any time, at most one is active.  The
       "stack" aspect of the api is designed to support "uninstallation",
       as will be described below.

       Registration stacks manage registrations.  They don't really care
       what registrations are.

         >>> from zope.app.registration import interfaces

         >>> class Registration(object):
         ...
         ...     def __init__(self, name):
         ...         self.name = name
         ...         self.active = False
         ...
         ...     def __repr__(self):
         ...         return self.name
         ...

       When a registration is activated or deactivated, an event is published
       to which one can subscribe; in our case the registration components
       themselves subscribe to these events to set their status.
         
         >>> def setActive(event):
         ...     event.object.active = True
         >>> subscribe((interfaces.IRegistrationActivatedEvent,), None,
         ...           setActive)
         
         >>> def unsetActive(event):
         ...     event.object.active = False
         >>> subscribe((interfaces.IRegistrationDeactivatedEvent,), None,
         ...           unsetActive)


       We create a registration stack by providing it with a parent:

         >>> from zope.app.registration.registration import RegistrationStack 
         >>> stack = RegistrationStack(42)
         >>> stack.__parent__
         42

       If a stack doesn't have any registrations, it's false:

         >>> bool(stack)
         False

       And it has no active registration:

         >>> stack.active()

       We can register a registration:

         >>> r1 = Registration('r1')
         >>> stack.register(r1)

       and then the stack is true:

         >>> bool(stack)
         True

       But we still don't have an active registration:

         >>> stack.active()

       Until we activate one:

         >>> stack.activate(r1)
         >>> stack.active()
         r1

       at which point, the registration has been notified that it is
       active:

         >>> r1.active
         True

       We can't activate a registration unless it's registered:

         >>> r2 = Registration('r2')
         >>> stack.activate(r2)
         Traceback (most recent call last):
         ...
         ValueError: ('Registration to be activated is not registered', r2)

         >>> stack.register(r2)
         >>> stack.activate(r2)

       Note that activating r2, deactivated r1:

         >>> r1.active
         False

       We can get status on the stack by calling it's info method:

         >>> for info in stack.info():
         ...     print info['registration'], info['active']
         r2 True
         r1 False

       So why is this a stack? Unregistering an object is a bit like
       popping an element. Suppose we unregister r2:

         >>> stack.unregister(r2)

       Whenever we unregister an object, we make the object that was
       previously active active again:

         >>> stack.active()
         r1

         >>> r1.active
         True

       Now, let's deactivate r1:

         >>> stack.deactivate(r1)
         >>> stack.active()
         >>> r1.active
         False

       And register and activate r2:

         >>> stack.register(r2)
         >>> stack.activate(r2)
         >>> stack.active()
         r2

       Now, if we unregister r2:

         >>> stack.unregister(r2)

       We won't have an active registration:

         >>> stack.active()

       Because there wasn't an active registration before we made r2
       active.
       """

#     The invariants for _data are as follows:
#
#         (1) The last element (if any) is not None
#
#         (2) No value occurs more than once
#
#         (3) Each value except None is a relative path from the nearest
#             service manager to an object implementing IRegistration

    implements(interfaces.IRegistrationStack)

    def __init__(self, container):
        self.__parent__ = container
        self.data = ()

    def register(self, registration):
        data = self.data
        if data:
            if registration in data:
                return # already registered
        else:
            # Nothing registered. Need to stick None in front so that nothing
            # is active.
            data = (None, )

        self.data = data + (registration, )

    def unregister(self, registration):
        data = self.data
        if data:
            if data[0] == registration:
                # It is active!
                data = data[1:]
                self.data = data

                # Tell it that it is no longer active
                self._deactivate(registration)

                if data and data[0] is not None:
                    # Activate the newly active component
                    self._activate(data[0])
            else:
                # Remove it from our data
                data = tuple([item for item in data if item != registration])

                # Check for trailing None
                if data and data[-1] is None:
                    data = data[:-1]

                self.data = data

    def registered(self, registration):
        return registration in self.data

    def _activate(self, registration):
        zope.event.notify(RegistrationActivatedEvent(registration))
        # BBB: Depraction warningl 12/05/2004
        if hasattr(registration, 'activated'):
            warnings.warn(
                "activated() deprected. Subscribe to "
                "IRegistrationActivatedEvent instead.",
                DeprecationWarning, stacklevel=3,
                )
            registration.activated()

    def _deactivate(self, registration):
        zope.event.notify(RegistrationDeactivatedEvent(registration))
        # BBB: Depraction warningl 12/05/2004
        if hasattr(registration, 'deactivated'):
            warnings.warn(
                "deactivated() deprected. Subscribe to "
                "IRegistrationDeactivatedEvent instead.",
                DeprecationWarning, stacklevel=3,
                )
            registration.deactivated()

    def activate(self, registration):
        data = self.data

        if registration is None and not data:
            return # already in the state we want

        if registration is None or registration in data:
            old = data[0]
            if old == registration:
                return # already active

            # Insert it in front, removing it from back
            data = ((registration, ) +
                    tuple([item
                           for item in data
                           if item != registration])
                    )

            # Check for trailing None
            if data[-1] == None:
                data = data[:-1]

            # Write data back
            self.data = data

            if old is not None:
                # Deactivated the currently active component
                self._deactivate(old)

            if registration is not None:
                # Tell it that it is now active
                self._activate(registration)

        else:
            raise ValueError(
                "Registration to be activated is not registered",
                registration)

    def deactivate(self, registration):
        data = self.data

        if registration not in data:
            raise ValueError(
                "Registration to be deactivated is not registered",
                registration)

        if data[0] != registration:
            return # already inactive

        if None not in data:
            # Append None
            data += (None,)

        # Move it to the end
        data = data[1:] + data[:1]

        # Write data back
        self.data = data

        # Tell it that it is no longer active
        self._deactivate(registration)

        if data[0] is not None:
            # Activate the newly active component
            self._activate(data[0])

    def active(self):
        data = self.data
        if data:
            return data[0]
        return None

    def __nonzero__(self):
        return bool(self.data)

    def info(self):
        data = self.data
        result = [{'active': False,
                   'registration': registration,
                  }
                  for registration in data
                 ]

        if result:
            result[0]['active'] = True

        return [r for r in result if r['registration'] is not None]

    #########################################################################
    # BBB: Backward compat
    #
    def data(self):
        # Need to convert old path-based data to object-based data
        # It won't affect new objects that get instance-based data attrs
        # on construction.

        data = []
        sm = zapi.getServices(self)
        for path in self._data:
            if isinstance(path, basestring):
                try:
                    data.append(zapi.traverse(sm, path))
                except KeyError:
                    # ignore objects we can't get to
                    raise # for testing
            else:
                data.append(path)

        return tuple(data)

    data = zope.cachedescriptors.property.CachedProperty(data)
    #
    #########################################################################


#############################################################################
# The functionality provided by this class can is better implemented by
# subscribing to the RegistrationActivatedEvent and
# RegistrationDeactivatedEvent.
class NotifyingRegistrationStack(RegistrationStack):
    """Notifying registration registry implemention

       First, see RegistrationStack.

       A notifying registration stack notifies both the registration
       *and* the stacks parent when it changes.  It notifies the
       parent by calling nothingActivated and notifyDeactivated:

         >>> class Parent(object):
         ...
         ...     active = deactive = None
         ...
         ...     def notifyActivated(self, stack, registration):
         ...         self.active = registration
         ...
         ...     def notifyDeactivated(self, stack, registration):
         ...         self.active = None
         ...         self.deactive = registration


       To see this, we'll go through the same scenario we went through
       in the RegistrationStack documentation.
       A registration stack provides support for a collection of

         >>> from zope.app.registration import interfaces
         >>> class Registration(object):
         ...
         ...     def __init__(self, name):
         ...         self.name = name
         ...         self.active = False
         ...
         ...     def __repr__(self):
         ...         return self.name

         >>> def setActive(event):
         ...     event.object.active = True
         >>> subscribe((interfaces.IRegistrationActivatedEvent,), None,
         ...           setActive)
         
         >>> def unsetActive(event):
         ...     event.object.active = False
         >>> subscribe((interfaces.IRegistrationDeactivatedEvent,), None,
         ...           unsetActive)

       We create a registration stack by providing it with a parent:

         >>> parent = Parent()
         >>> from zope.app.registration import registration
         >>> stack = registration.NotifyingRegistrationStack(parent)

       We can register a registration:

         >>> r1 = Registration('r1')
         >>> stack.register(r1)

       But we still don't have an active registration:

         >>> stack.active()
         >>> parent.active

       Until we activate one:

         >>> stack.activate(r1)
         >>> parent.active
         r1

       if we activate a new registration:

         >>> r2 = Registration('r2')
         >>> stack.register(r2)
         >>> stack.activate(r2)

       The parent will be notified of the activation and the
       deactivation:

         >>> parent.active
         r2
         >>> parent.deactive
         r1

       If we unregister r2, it will become inactive and the parent
       will be notified, but whenever we unregister an object, we make
       the object that was previously active active again:

         >>> stack.unregister(r2)
         >>> parent.active
         r1
         >>> parent.deactive
         r2

       Now, let's deactivate r1:

         >>> stack.deactivate(r1)
         >>> parent.active
         >>> parent.deactive
         r1

       And register and activate r2:

         >>> stack.register(r2)
         >>> stack.activate(r2)
         >>> parent.active
         r2

       Now, if we unregister r2:

         >>> stack.unregister(r2)

       We won't have an active registration:

         >>> parent.active
         >>> parent.deactive
         r2

       Because there wasn't an active registration before we made r2
       active.
       """
    def _activate(self, registration):
        super(NotifyingRegistrationStack, self)._activate(registration)
        self.__parent__.notifyActivated(self, registration)

    def _deactivate(self, registration):
        super(NotifyingRegistrationStack, self)._activate(registration)
        self.__parent__.notifyDeactivated(self, registration)
#############################################################################


def SimpleRegistrationRemoveSubscriber(registration, event):
    """Receive notification of remove event."""

    services = getLocalServices(registration)
    removed = event.object
    if (services == removed) or inside(services, removed):
        # we don't really care if the rigistration is active or
        # registered, since the site is going away.
        return

    objectstatus = registration.status

    if objectstatus == interfaces.ActiveStatus:
        try:
            objectpath = zapi.getPath(registration)
        except: # XXX
            objectpath = str(registration)
        raise DependencyError("Can't delete active registration (%s)"
                              % objectpath)
    elif objectstatus == interfaces.RegisteredStatus:
        registration.status = interfaces.UnregisteredStatus


class SimpleRegistration(Persistent, Contained):
    """Registration objects that just contain registration data"""

    # We are including IAttributeAnnotatable here because we want all
    # of the subclasses to get it and we don't really need to be
    # flexible about the policy here. At least we don't *think* we
    # do. :)
    implements(interfaces.IRegistration, IAttributeAnnotatable)

    status = RegistrationStatusProperty()

    # Methods from IRegistration

    # BBB: Deprecated on 12/05/2004
    # def activated(self):
    #     pass
    #
    # def deactivated(self):
    #     pass

    def usageSummary(self):
        return self.__class__.__name__

    def implementationSummary(self):
        return ""


# BBB: 12/05/2004
NULL_COMPONENT = object()

class ComponentRegistration(SimpleRegistration):
    """Component registration.

    Subclasses should define a getInterface() method returning the interface
    of the component.
    """

    implements(interfaces.IComponentRegistration)

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

    def implementationSummary(self):
        return zapi.getPath(self.component)

    ###########################################################################
    # BBB: Backward compatibility from 12/05/2004
    def getComponent(self):
        warnings.warn(
            "`getComponent()` is deprecated, since the component is now "
            "available directly via `component`. Also, you should not use the "
            "not use `componentPath` anymore, since it is deprecated.",
            DeprecationWarning, stacklevel=2,
            )
        return self.__BBB_getComponent()

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
        service_manager = zapi.getServices(self)
        
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
        warnings.warn(
            "`componentPath` is deprecated. You can get to the component "
            "directly by accessing `component`.",
            DeprecationWarning, stacklevel=3,
            )
        if self._BBB_componentPath is not None:
            return self._BBB_componentPath
        return '/' + '/'.join(zapi.getPath(self.component))

    def __BBB_setComponentPath(self, path):
        warnings.warn(
            "`componentPath` is deprecated. You can get to the component "
            "directly by accessing `component`.",
            DeprecationWarning, stacklevel=3,
            )
        self._component = NULL_COMPONENT
        self._BBB_componentPath = path

    componentPath = property(__BBB_getComponentPath, __BBB_setComponentPath)

    def __setstate__(self, dict):
        super(ComponentRegistration, self).__setstate__(dict)
        # For some reason the component path is not set correctly by the
        # default __setstate__ mechanism. 
        if 'componentPath' in dict:
            self._component = NULL_COMPONENT
            self._BBB_componentPath = dict['componentPath']

        if isinstance(self._BBB_componentPath, (str, unicode)):
            self._component = NULL_COMPONENT
    
    ###########################################################################


def ComponentRegistrationRemoveSubscriber(component_registration, event):
    """Receive notification of remove event."""
    component = component_registration.component
    dependents = IDependable(component)
    objectpath = zapi.getPath(component_registration)
    dependents.removeDependent(objectpath)
    # Also update usage, if supported
    adapter = interfaces.IRegistered(component, None)
    if adapter is not None:
        adapter.removeUsage(zapi.getPath(component_registration))

def ComponentRegistrationAddSubscriber(component_registration, event):
    """Receive notification of add event."""
    component = component_registration.component
    dependents = IDependable(component)
    objectpath = zapi.getPath(component_registration)
    dependents.addDependent(objectpath)
    # Also update usage, if supported
    adapter = interfaces.IRegistered(component, None)
    if adapter is not None:
        adapter.addUsage(objectpath)

def RegisterableMoveSubscriber(registerable, event):
    """Updates componentPath for registrations on component rename."""
    if event.oldParent is not None and event.newParent is not None:
        if event.oldParent is not event.newParent:
            raise DependencyError(
                "Can't move a registered component from its container.")

from zope.app.dependable import PathSetAnnotation

class Registered(PathSetAnnotation):
    """An adapter from IRegisterable to IRegistered.

    This class is the only place that knows how 'Registered'
    data is represented.
    """
    implements(interfaces.IRegistered)

    __used_for__ = interfaces.IRegisterable

    # We want to use this key:
    #   key = "zope.app.registration.Registered"
    # But we have existing annotations with the following key, so we'll keep
    # it. :(
    key = "zope.app.services.configuration.UseConfiguration"

    addUsage = PathSetAnnotation.addPath
    removeUsage = PathSetAnnotation.removePath
    usages = PathSetAnnotation.getPaths

    def registrations(self):
        return [zapi.traverse(self.context, path)
                for path in self.getPaths()]

class RegisterableCopier(ObjectCopier):
    """Copies registerable components.

    Performs the additional step of removing existing registered usages
    for the new copy.
    """
    __used_for__ = interfaces.IRegisterable

    def _configureCopy(self, copy, target, new_name):
        ObjectCopier._configureCopy(self, copy, target, new_name)
        registered = interfaces.IRegistered(copy, None)
        if registered is not None:
            for usage in registered.usages():
                registered.removeUsage(usage)

class RegistrationManager(Persistent, Contained):
    """Registration manager

    Manages registrations within a package.
    """
    implements(interfaces.IRegistrationManager)

    def __init__(self):
        self._data = ()

    def __getitem__(self, key):
        "See IItemContainer"
        v = self.get(key)
        if v is None:
            raise KeyError, key
        return v

    def get(self, key, default=None):
        "See IReadMapping"
        for k, v in self._data:
            if k == key:
                return v
        return default

    def __contains__(self, key):
        "See IReadMapping"
        return self.get(key) is not None

    def keys(self):
        "See IEnumerableMapping"
        return [k for k, v in self._data]

    def __iter__(self):
        return iter(self.keys())

    def values(self):
        "See IEnumerableMapping"
        return [v for k, v in self._data]

    def items(self):
        "See IEnumerableMapping"
        return self._data

    def __len__(self):
        "See IEnumerableMapping"
        return len(self._data)

    def __setitem__(self, key, v):
        setitem(self, self.__setitem, key, v)

    def __setitem(self, key, v):
        if key in self:
            raise DuplicationError(key)
        self._data += ((key, v), )

    def addRegistration(self, object):
        "See IWriteContainer"
        key = self._chooseName('', object)
        self[key] = object
        return key

    def _chooseName(self, name, object):
        if not name:
            name = object.__class__.__name__

        i = 1
        n = name
        while n in self:
            i += 1
            n = name + str(i)

        return n

    def __delitem__(self, key):
        "See IWriteContainer"
        uncontained(self[key], self, key)
        self._data = tuple(
            [item
             for item in self._data
             if item[0] != key]
            )

    def moveTop(self, names):
        self._data = tuple(
            [item for item in self._data if (item[0] in names)]
            +
            [item for item in self._data if (item[0] not in names)]
            )

    def moveBottom(self, names):
        self._data = tuple(
            [item for item in self._data if (item[0] not in names)]
            +
            [item for item in self._data if (item[0] in names)]
            )

    def _moveUpOrDown(self, names, direction):
        # Move each named item by one position. Note that this
        # might require moving some unnamed objects by more than
        # one position.

        indexes = {}

        # Copy named items to positions one less than they currently have
        i = -1
        for item in self._data:
            i += 1
            if item[0] in names:
                j = max(i + direction, 0)
                while j in indexes:
                    j += 1

                indexes[j] = item

        # Fill in the rest where there's room.
        i = 0
        for item in self._data:
            if item[0] not in names:
                while i in indexes:
                    i += 1
                indexes[i] = item

        items = indexes.items()
        items.sort()

        self._data = tuple([item[1] for item in items])

    def moveUp(self, names):
        self._moveUpOrDown(names, -1)

    def moveDown(self, names):
        self._moveUpOrDown(names, 1)


class RegisterableContainer(object):
    """Mix-in to implement IRegisterableContainer
    """
    implements(interfaces.IRegisterableContainer)

    def __init__(self):
        super(RegisterableContainer, self).__init__()
        rm = RegistrationManager()
        rm.__parent__ = self
        rm.__name__ = 'RegistrationManager'
        zope.event.notify(objectevent.ObjectCreatedEvent(rm))
        self[rm.__name__] = rm

    def __delitem__(self, name):
        """Delete an item, but not if it's the last registration manager
        """
        item = self[name]
        if interfaces.IRegistrationManager.providedBy(item):
            # Check to make sure it's not the last one
            if len([i for i in self.values()
                    if interfaces.IRegistrationManager.providedBy(i)
                    ]
                   ) < 2:
                raise interfaces.NoRegistrationManagerError(
                    "Can't delete the last registration manager")
        super(RegisterableContainer, self).__delitem__(name)

    def getRegistrationManager(self):
        """Get a registration manager
        """
        # Get the registration manager for this folder
        for name in self:
            item = self[name]
            if interfaces.IRegistrationManager.providedBy(item):
                # We found one. Get it in context
                return item
        else:
            raise interfaces.NoRegistrationManagerError(
                "Couldn't find an registration manager")

    def findModule(self, name):
        # Used by the persistent modules import hook

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


        # See if out container is a RegisterableContainer:
        c = self.__parent__
        if interfaces.IRegisterableContainer.providedBy(c):
            return c.findModule(name)

        # Use sys.modules in lieu of module service:
        module = sys.modules.get(name)
        if module is not None:
            return module

        raise ImportError(name)


    def resolve(self, name):
        l = name.rfind('.')
        mod = self.findModule(name[:l])
        return getattr(mod, name[l+1:])
