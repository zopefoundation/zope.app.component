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
"""Generic Components ZCML Handlers

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface
from zope.component.service import UndefinedService
from zope.configuration.exceptions import ConfigurationError
from zope.security.checker import InterfaceChecker, CheckerPublic, \
     Checker, NamesChecker
from zope.security.proxy import Proxy, ProxyFactory
from zope.component.interfaces import IFactory

from zope.app import zapi
from zope.app.component.interface import queryInterface
from zope.app.servicenames import Adapters, Presentation
from zope.app.security.adapter import TrustedAdapterFactory

PublicPermission = 'zope.Public'

# I prefer the indirection (using getService and getServices vs.
# directly importing the various services)  not only because it makes
# unit tests easier, but also because it reinforces that the services
# should always be obtained through the
# IPlacefulComponentArchitecture interface methods.

# But these services aren't placeful! And we need to get at things that
# normal service clients don't need!   Jim


def handler(serviceName, methodName, *args, **kwargs):
    method=getattr(zapi.getGlobalService(serviceName), methodName)
    method(*args, **kwargs)

# We can't use the handler for serviceType, because serviceType needs
# the interface service.
from zope.app.component.interface import provideInterface

def managerHandler(methodName, *args, **kwargs):
    method=getattr(zapi.getGlobalServices(), methodName)
    method(*args, **kwargs)

def interface(_context, interface, type=None):
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = ('', interface, type)
        )


def proxify(ob, checker):
    """Try to get the object proxied with the `checker`, but not too soon

    We really don't want to proxy the object unless we need to.
    """

    try:
        ob.__Security_checker__ = checker
    except AttributeError:
        ob = Proxy(ob, checker)

    return ob

def subscriber(_context, factory, for_, provides=None, permission=None,
               trusted=False):
    factory = [factory]

    if permission is not None:
        if permission == PublicPermission:
            permission = CheckerPublic
        checker = InterfaceChecker(provides, permission)
        factory.append(lambda c: proxify(c, checker))

    for_ = tuple(for_)

    # Generate a single factory from multiple factories:
    factories = factory
    if len(factories) == 1:
        factory = factories[0]
    elif len(factories) < 1:
        raise ValueError("No factory specified")
    elif len(factories) > 1 and len(for_) != 1:
        raise ValueError("Can't use multiple factories and multiple for")
    else:
        def factory(ob):
            for f in factories:
                ob = f(ob)
            return ob

    if trusted:
        factory = TrustedAdapterFactory(factory)

    _context.action(
        discriminator = None,
        callable = handler,
        args = (Adapters, 'subscribe',
                for_, provides, factory),
        )

    if provides is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', provides)
            )
    
    # For each interface, state that the adapter provides that interface.
    for iface in for_:
        if iface is not None:
            _context.action(
                discriminator = None,
                callable = provideInterface,
                args = ('', iface)
                )

def adapter(_context, factory, provides, for_, permission=None, name='',
            trusted=False):
    if permission is not None:
        if permission == PublicPermission:
            permission = CheckerPublic
        checker = InterfaceChecker(provides, permission)
        factory.append(lambda c: proxify(c, checker))

    for_ = tuple(for_)

    # Generate a single factory from multiple factories:
    factories = factory
    if len(factories) == 1:
        factory = factories[0]
    elif len(factories) < 1:
        raise ValueError("No factory specified")
    elif len(factories) > 1 and len(for_) != 1:
        raise ValueError("Can't use multiple factories and multiple for")
    else:
        def factory(ob):
            for f in factories:
                ob = f(ob)
            return ob
        # Store the original factory for documentation
        factory.factory = factories[0]

    if trusted:
        factory = TrustedAdapterFactory(factory)

    _context.action(
        discriminator = ('adapter', for_, provides, name),
        callable = handler,
        args = (Adapters, 'register',
                for_, provides, name, factory, _context.info),
        )
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = ('', provides)
               )
    if for_:
        for iface in for_:
            if iface is not None:
                _context.action(
                    discriminator = None,
                    callable = provideInterface,
                    args = ('', iface)
                    )

def utility(_context, provides, component=None, factory=None,
            permission=None, name=''):
    if factory:
        if component:
            raise TypeError("Can't specify factory and component.")
        component = factory()

    if permission is not None:
        if permission == PublicPermission:
            permission = CheckerPublic
        checker = InterfaceChecker(provides, permission)

        component = proxify(component, checker)

    _context.action(
        discriminator = ('utility', provides, name),
        callable = handler,
        args = ('Utilities', 'provideUtility',
                provides, component, name),
        )
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = (provides.__module__ + '.' + provides.getName(), provides)
               )

def factory(_context, component, id, title=None, description=None):
    if title is not None:
        component.title = title
        
    if description is not None:
        component.description = description

    utility(_context, IFactory, component,
            permission=PublicPermission, name=id)


def _checker(_context, permission, allowed_interface, allowed_attributes):
    if (not allowed_attributes) and (not allowed_interface):
        allowed_attributes = ["__call__"]

    if permission == PublicPermission:
        permission = CheckerPublic

    require={}
    if allowed_attributes:
        for name in allowed_attributes:
            require[name] = permission
    if allowed_interface:
        for i in allowed_interface:
            for name in i.names(all=True):
                require[name] = permission

    checker = Checker(require)
    return checker

def resource(_context, factory, type, name, layer='default',
             permission=None,
             allowed_interface=None, allowed_attributes=None,
             provides=Interface):

    if ((allowed_attributes or allowed_interface)
        and (not permission)):
        raise ConfigurationError(
            "Must use name attribute with allowed_interface or "
            "allowed_attributes"
            )

    if permission:

        checker = _checker(_context, permission,
                           allowed_interface, allowed_attributes)

        def proxyResource(request, factory=factory, checker=checker):
            return proxify(factory(request), checker)

        factory = proxyResource

    _context.action(
        discriminator = ('resource', name, type, layer, provides),
        callable = handler,
        args = (Presentation, 'provideResource',
                name, type, factory, layer, provides),
        )
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = (type.__module__ + '.' + type.__name__, type)
               )
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = (provides.__module__ + '.' + provides.__name__, type)
               )

def view(_context, factory, type, name, for_, layer='default',
         permission=None, allowed_interface=None, allowed_attributes=None,
         provides=Interface):

    if ((allowed_attributes or allowed_interface)
        and (not permission)):
        raise ConfigurationError(
            "Must use name attribute with allowed_interface or "
            "allowed_attributes"
            )

    if not factory:
        raise ConfigurationError("No view factory specified.")

    if permission:

        checker = _checker(_context, permission,
                           allowed_interface, allowed_attributes)

        class ProxyView(object):
            """Class to create simple proxy views."""

            def __init__(self, factory, checker):
                self.factory = factory
                self.checker = checker

            def __call__(self, *objects):
                return proxify(self.factory(*objects), self.checker)

        factory[-1] = ProxyView(factory[-1], checker)


    if not for_:
        raise ValueError("No for interfaces specified");
    for_ = tuple(for_)

    # Generate a single factory from multiple factories:
    factories = factory
    if len(factories) == 1:
        factory = factories[0]
    elif len(factories) < 1:
        raise ValueError("No factory specified")
    elif len(factories) > 1 and len(for_) > 1:
        raise ValueError("Can't use multiple factories and multiple for")
    else:
        def factory(ob, request):
            for f in factories[:-1]:
                ob = f(ob)
            return factories[-1](ob, request)

    _context.action(
        discriminator = ('view', for_, name, type, layer, provides),
        callable = handler,
        args = (Presentation, 'provideAdapter',
                type, factory, name, for_, provides, layer, _context.info),
        )
    if type is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', type)
            )
        
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = ('', provides)
        )

    if for_ is not None:
        for iface in for_:
            if iface is not None:
                _context.action(
                    discriminator = None,
                    callable = provideInterface,
                    args = ('', iface)
                    )

def defaultView(_context, type, name, for_):

    _context.action(
        discriminator = ('defaultViewName', for_, type, name),
        callable = handler,
        args = (Presentation, 'setDefaultViewName', for_, type, name),
        )
    
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = ('', type)
        )

    for iface in for_:
        if iface is not None:
            _context.action(
                discriminator = None,
                callable = provideInterface,
                args = ('', iface)
                )

def serviceType(_context, id, interface):
    _context.action(
        discriminator = ('serviceType', id),
        callable = managerHandler,
        args = ('defineService', id, interface),
        )

    if interface.__name__ not in ['IUtilityService']:
        _context.action(
            discriminator = None,
             callable = provideInterface,
             args = (interface.__module__+'.'+interface.getName(),
                     interface)
             )

def provideService(serviceType, component, permission):
    # This is needed so we can add a security proxy.
    # We have to wait till execution time so we can find out the interface.
    # Waaaa.

    service_manager = zapi.getGlobalServices()

    if permission:
        for stype, interface in service_manager.getServiceDefinitions():
            if stype == serviceType:
                break
        else:
            raise UndefinedService(serviceType)

        if permission == PublicPermission:
            permission = CheckerPublic

        checker = InterfaceChecker(interface, permission)

        try:
            component.__Security_checker__ = checker
        except: # too bad exceptions aren't more predictable
            component = proxify(component, checker)

    service_manager.provideService(serviceType, component)

def service(_context, serviceType, component=None, permission=None,
            factory=None):
    if factory:
        if component:
            raise TypeError("Can't specify factory and component.")

        component = factory()

    _context.action(
        discriminator = ('service', serviceType),
        callable = provideService,
        args = (serviceType, component, permission),
        )
