##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from zope.configuration.exceptions import ConfigurationError
from zope.security.proxy import Proxy
from zope.component import getService, getServiceManager
from zope.configuration import namespace
from zope.interface import Interface
from zope.configuration.action import Action
from zope.security.checker \
     import InterfaceChecker, CheckerPublic, NamesChecker, Checker
from zope.app.security.registries.permissionregistry import permissionRegistry
from zope.component.service \
     import UndefinedService

# I prefer the indirection (using getService and getServiceManager vs.
# directly importing the various services)  not only because it makes
# unit tests easier, but also because it reinforces that the services
# should always be obtained through the
# IPlacefulComponentArchitecture interface methods

# But these services aren't placeful! And we need to get at things that
# normal service clients don't need!   Jim


def handler(serviceName, methodName, *args, **kwargs):
    method=getattr(getService(None, serviceName), methodName)
    method(*args, **kwargs)

# We can't use the handler for serviceType, because serviceType needs
# the interface service.
from zope.app.component.globalinterfaceservice import provideInterface

def checkingHandler(permission=None, *args, **kw):
    """Check if permission is defined"""
    if permission is not None:
        permissionRegistry.ensurePermissionDefined(permission)
    handler(*args, **kw)

def managerHandler(methodName, *args, **kwargs):
    method=getattr(getServiceManager(None), methodName)
    method(*args, **kwargs)

def interface(_context, interface):
    interface = _context.resolve(interface)
    return [
        Action(
          discriminator = None,
          callable = handler,
          args = ('Interfaces', 'provideInterface', '', interface)
        ),
      ]


def adapter(_context, factory, provides, for_=None, permission=None, name=''):
    if for_ is not None: for_ = _context.resolve(for_)
    provides = _context.resolve(provides)
    factory = map(_context.resolve, factory.split())

    if permission is not None:
        if permission == 'zope.Public':
            permission = CheckerPublic
        checker = InterfaceChecker(provides, permission)
        factory.append(lambda c: Proxy(c, checker))
    actions=[
        Action(
            discriminator = ('adapter', for_, provides, name),
            callable = checkingHandler,
            args = (permission, 'Adapters', 'provideAdapter',
                    for_, provides, factory, name),
               ),
        Action(
            discriminator = None,
            callable = handler,
            args = ('Interfaces', 'provideInterface', '', provides)
              )
              ]
    if for_ is not None:
        actions.append
        (
        Action(
            discriminator = None,
            callable = handler,
            args = ('Interfaces', 'provideInterface', '', for_)
              )
         )

    return actions


def utility(_context, provides, component=None, factory=None,
            permission=None, name=''):
    provides = _context.resolve(provides)

    if factory:
        if component:
            raise TypeError("Can't specify factory and component.")

        component = _context.resolve(factory)()
    else:
        component = _context.resolve(component)

    if permission is not None:
        if permission == 'Zope.Public':
            permission = CheckerPublic
        checker = InterfaceChecker(provides, permission)

        component = Proxy(component, checker)

    return [
        Action(
            discriminator = ('utility', provides, name),
            callable = checkingHandler,
            args = (permission, 'Utilities', 'provideUtility',
                    provides, component, name),
            ),
        Action(
            discriminator = None,
            callable = handler,
            args = ('Interfaces', 'provideInterface',
                    provides.__module__+'.'+provides.__name__, provides)
              )
        ]


def factory(_context, component, id=None):
    if id is None:
        id = component

    component = _context.resolve(component)

    return [
        Action(
            discriminator = ('factory', id),
            callable = handler,
            args = ('Factories', 'provideFactory', id, component),
            )
        ]

def _checker(_context, permission, allowed_interface, allowed_attributes):
    if (not allowed_attributes) and (not allowed_interface):
        allowed_attributes = "__call__"

    if permission == 'zope.Public':
        permission = CheckerPublic

    require={}
    for name in (allowed_attributes or '').split():
        require[name] = permission
    if allowed_interface:
        for name in _context.resolve(allowed_interface).names(1):
            require[name] = permission

    checker = Checker(require.get)

    return checker

def resource(_context, factory, type, name, layer='default',
             permission=None,
             allowed_interface=None, allowed_attributes=None):

    if ((allowed_attributes or allowed_interface)
        and (not permission)):
        raise ConfigurationError(
            "Must use name attribute with allowed_interface or "
            "allowed_attributes"
            )


    type = _context.resolve(type)
    factory = _context.resolve(factory)


    if permission:

        checker = _checker(_context, permission,
                           allowed_interface, allowed_attributes)

        def proxyResource(request, factory=factory, checker=checker):
            return Proxy(factory(request), checker)

        factory = proxyResource

    return [
        Action(
            discriminator = ('resource', name, type, layer),
            callable = checkingHandler,
            args = (permission, 'Resources','provideResource',
                    name, type, factory, layer),
            ),
        Action(
            discriminator = None,
            callable = handler,
            args = ('Interfaces', 'provideInterface',
                    type.__module__+'.'+type.__name__, type)
              )
        ]

def view(_context, factory, type, name, for_=None, layer='default',
         permission=None, allowed_interface=None, allowed_attributes=None):

    if ((allowed_attributes or allowed_interface)
        and (not permission)):
        raise ConfigurationError(
            "Must use name attribute with allowed_interface or "
            "allowed_attributes"
            )

    if for_ is not None: for_ = _context.resolve(for_)
    type = _context.resolve(type)

    factory = map(_context.resolve, factory.strip().split())
    if not factory:
        raise ConfigurationError("No view factory specified.")

    if permission:

        checker = _checker(_context, permission,
                           allowed_interface, allowed_attributes)

        def proxyView(context, request, factory=factory[-1], checker=checker):
            return Proxy(factory(context, request), checker)

        factory[-1] = proxyView

    actions=[
        Action(
            discriminator = ('view', for_, name, type, layer),
            callable = checkingHandler,
            args = (permission, 'Views','provideView', for_, name,
                    type, factory, layer),
            ),
        Action(
            discriminator = None,
            callable = handler,
            args = ('Interfaces', 'provideInterface',
                    type.__module__+'.'+type.__name__, type)
            )
            ]
    if for_ is not None:
        actions.append
        (
        Action(
            discriminator = None,
            callable = handler,
            args = ('Interfaces', 'provideInterface',
                    for_.__module__+'.'+for_.__name__,
                    for_)
              )
         )

    return actions

def defaultView(_context, type, name, for_=None, **__kw):

    if __kw:
        actions = view(_context, type=type, name=name, for_=for_, **__kw)
    else:
        actions = []

    if for_ is not None:
        for_ = _context.resolve(for_)
    type = _context.resolve(type)

    actions += [
        Action(
        discriminator = ('defaultViewName', for_, type, name),
        callable = handler,
        args = ('Views','setDefaultViewName', for_, type, name),
        ),
        Action(
            discriminator = None,
            callable = handler,
            args = ('Interfaces', 'provideInterface',
                    type.__module__+'.'+type.__name__, type)
            )
               ]
    if for_ is not None:
        actions.append
        (
        Action(
            discriminator = None,
            callable = handler,
            args = ('Interfaces', 'provideInterface',
                    for_.__module__+'.'+for_.__name__, for_)
              )
         )

    return actions

def serviceType(_context, id, interface):
    interface = _context.resolve(interface)
    return [
        Action(
            discriminator = ('serviceType', id),
            callable = managerHandler,
            args = ('defineService', id, interface),
            ),
        Action(
            discriminator = None,
            callable = provideInterface,
            args = (interface.__module__+'.'+interface.__name__,
                    interface)
            )
        ]

def provideService(serviceType, component, permission):
    # This is needed so we can add a security proxy.
    # We have to wait till execution time so we can find out the interface.
    # Waaaa.

    service_manager = getServiceManager(None)

    if permission:

        for stype, interface in service_manager.getServiceDefinitions():
            if stype == serviceType:
                break
        else:
            raise UndefinedService(serviceType)

        if permission == 'zope.Public':
            permission = CheckerPublic

        checker = InterfaceChecker(interface, permission)

        try:
            component.__Security_checker__ = checker
        except: # too bad exceptions aren't more predictable
            component = Proxy(component, checker)

    service_manager.provideService(serviceType, component)

def service(_context, serviceType, component=None, permission=None,
            factory=None):
    if factory:
        if component:
            raise TypeError("Can't specify factory and component.")

        component = _context.resolve(factory)()
    else:
        component = _context.resolve(component)

    return [
        Action(
            discriminator = ('service', serviceType),
            callable = provideService,
            args = (serviceType, component, permission),
            )
        ]

def skin(_context, name, layers, type):
    type = _context.resolve(type)
    if ',' in layers:
        raise TypeError("Commas are not allowed in layer names.")

    layers = layers.strip().split()
    actions = [
        Action(
            discriminator = ('skin', name, type),
            callable = handler,
            args = ('Skins','defineSkin',name, type, layers)
              ),
        Action(
            discriminator = None,
            callable = handler,
            args = ('Interfaces', 'provideInterface',
                    type.__module__+'.'+type.__name__, type)
              )
             ]
    return actions
