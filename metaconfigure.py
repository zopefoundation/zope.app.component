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
"""
$Id: metaconfigure.py,v 1.16 2003/08/04 15:07:54 philikon Exp $
"""

from zope.configuration.exceptions import ConfigurationError
from zope.security.proxy import Proxy, ProxyFactory
from zope.component import getService, getServiceManager
from zope.app.services.servicenames import Adapters, Interfaces, Skins
from zope.app.services.servicenames import Views, Resources, Factories
from zope.app.component.globalinterfaceservice import interfaceService
from zope.security.checker import InterfaceChecker, CheckerPublic, \
     Checker, NamesChecker
from zope.app.security.registries.permissionregistry import permissionRegistry
from zope.component.service import UndefinedService

PublicPermission = 'zope.Public'

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
    _context.action(
        discriminator = None,
        callable = handler,
        args = (Interfaces, 'provideInterface', '', interface)
        )

def adapter(_context, factory, provides, for_, permission=None, name=''):
    if permission is not None:
        if permission == PublicPermission:
            permission = CheckerPublic
        checker = InterfaceChecker(provides, permission)
        factory.append(lambda c: Proxy(c, checker))
    _context.action(
        discriminator = ('adapter', for_, provides, name),
        callable = checkingHandler,
        args = (permission, Adapters, 'provideAdapter',
                for_, provides, factory, name),
        )
    _context.action(
        discriminator = None,
        callable = handler,
        args = (Interfaces, 'provideInterface', '', provides)
        )
    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = handler,
            args = (Interfaces, 'provideInterface', '', for_)
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

        component = Proxy(component, checker)

    _context.action(
        discriminator = ('utility', provides, name),
        callable = checkingHandler,
        args = (permission, 'Utilities', 'provideUtility',
                provides, component, name),
        )
    _context.action(
        discriminator = None,
        callable = handler,
        args = (Interfaces, 'provideInterface',
                provides.__module__+'.'+provides.__name__, provides)
        )

def factory(_context, component, id=None, permission=None):
    _context.action(
        discriminator = ('factory', id),
        callable = provideFactory,
        args = (id, component, permission),
        )

def provideFactory(name, factory, permission):
    # make sure the permission is defined
    if permission is not None:
        permissionRegistry.ensurePermissionDefined(permission)

    if permission == PublicPermission:
        permission = CheckerPublic

    if permission:
        # XXX should getInterfaces be public, as below?
        factory = ProxyFactory(
            factory,
            NamesChecker(('getInterfaces',),
                         __call__=permission)
            )
    getService(None, Factories).provideFactory(name, factory)

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

    if permission:

        checker = _checker(_context, permission,
                           allowed_interface, allowed_attributes)

        def proxyResource(request, factory=factory, checker=checker):
            return Proxy(factory(request), checker)

        factory = proxyResource

    _context.action(
        discriminator = ('resource', name, type, layer),
        callable = checkingHandler,
        args = (permission, Resources,'provideResource',
                name, type, factory, layer),
        )
    _context.action(
        discriminator = None,
        callable = handler,
        args = (Interfaces, 'provideInterface',
                type.__module__+'.'+type.__name__, type)
        )

def view(_context, factory, type, name, for_, layer='default',
         permission=None, allowed_interface=None, allowed_attributes=None):

    if for_ == '*':
        for_ = None

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

        def proxyView(context, request, factory=factory[-1], checker=checker):
            return Proxy(factory(context, request), checker)

        factory[-1] = proxyView

    _context.action(
        discriminator = ('view', for_, name, type, layer),
        callable = checkingHandler,
        args = (permission, Views,'provideView', for_, name,
                type, factory, layer),
        )
    _context.action(
        discriminator = None,
        callable = handler,
        args = (Interfaces, 'provideInterface',
                type.__module__+'.'+type.__name__, type)
        )

    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = handler,
            args = (Interfaces, 'provideInterface',
                    for_.__module__+'.'+for_.__name__,
                    for_)
            )

def defaultView(_context, type, name, for_, **__kw):

    if for_ == '*':
        for_ = None

    if __kw:
        view(_context, type=type, name=name, for_=for_, **__kw)

    _context.action(
        discriminator = ('defaultViewName', for_, type, name),
        callable = handler,
        args = (Views,'setDefaultViewName', for_, type, name),
        )
    _context.action(
        discriminator = None,
        callable = handler,
        args = (Interfaces, 'provideInterface',
                type.__module__+'.'+type.__name__, type)
        )

    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = handler,
            args = (Interfaces, 'provideInterface',
                    for_.__module__+'.'+for_.__name__, for_)
            )

def serviceType(_context, id, interface):
    _context.action(
        discriminator = ('serviceType', id),
        callable = managerHandler,
        args = ('defineService', id, interface),
        )
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = (interface.__module__+'.'+interface.__name__,
                interface)
        )

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

        if permission == PublicPermission:
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

        component = factory()

    _context.action(
        discriminator = ('service', serviceType),
        callable = provideService,
        args = (serviceType, component, permission),
        )

def skin(_context, name, layers, type):
    if ',' in layers:
        raise TypeError("Commas are not allowed in layer names.")

    _context.action(
        discriminator = ('skin', name, type),
        callable = handler,
        args = (Skins,'defineSkin',name, type, layers)
        )

    _context.action(
        discriminator = None,
        callable = handler,
        args = (Interfaces, 'provideInterface',
                type.__module__+'.'+type.__name__, type)
        )
