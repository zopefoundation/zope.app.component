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
"""Generic Components ZCML Handlers

$Id: metaconfigure.py,v 1.27 2004/03/05 15:53:17 eddala Exp $
"""

from zope.configuration.exceptions import ConfigurationError
from zope.security.proxy import Proxy, ProxyFactory
from zope.component import getService, getServiceManager
from zope.component.factory import FactoryInfo
from zope.app.services.servicenames import Adapters
from zope.app.services.servicenames import Factories, Presentation
from zope.app.component.interface import queryInterface
from zope.security.checker import InterfaceChecker, CheckerPublic, \
     Checker, NamesChecker
from zope.app.security.registries.permissionregistry import permissionRegistry
from zope.component.service import UndefinedService
import zope.interface

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
from zope.app.component.interface import provideInterface

def checkingHandler(permission=None, *args, **kw):
    """Check if permission is defined"""
    if permission is not None:
        permissionRegistry.ensurePermissionDefined(permission)
    handler(*args, **kw)

def managerHandler(methodName, *args, **kwargs):
    method=getattr(getServiceManager(None), methodName)
    method(*args, **kwargs)

def interface(_context, interface, type=None):
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = ('', interface, type)
        )


def proxify(ob, checker):
    """Try to get the object proxied with the checker, but not too soon

    We really don't want to proxy the object unless we need to.
    """

    try:
        ob.__Security_checker__ = checker
    except AttributeError:
        ob = Proxy(ob, checker)

    return ob


def adapter(_context, factory, provides, for_, permission=None, name=''):
    if permission is not None:
        if permission == PublicPermission:
            permission = CheckerPublic
        checker = InterfaceChecker(provides, permission)
        factory.append(lambda c: proxify(c, checker))

        
    _context.action(
        discriminator = ('adapter', for_, provides, name),
        callable = checkingHandler,
        args = (permission, Adapters, 'provideAdapter',
                for_, provides, factory, name),
        )
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = ('', provides)
               )
    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
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
        callable = checkingHandler,
        args = (permission, 'Utilities', 'provideUtility',
                provides, component, name),
        )
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = (provides.__module__ + '.' + provides.getName(), provides)
               )

def factory(_context, component, id=None, title=None, description=None, 
            permission=None):
    _context.action(
        discriminator = ('factory', id),
        callable = provideFactory,
        args = (id, component, title, description, permission),
        )

def provideFactory(name, factory, title, description, permission):
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
    info = FactoryInfo(title, description)
    getService(None, Factories).provideFactory(name, factory, info)

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
             allowed_interface=None, allowed_attributes=None,
             provides=zope.interface.Interface):

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
        callable = checkingHandler,
        args = (permission, Presentation, 'provideResource',
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
         provides=zope.interface.Interface):

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
            return proxify(factory(context, request), checker)

        factory[-1] = proxyView

    _context.action(
        discriminator = ('view', for_, name, type, layer, provides),
        callable = checkingHandler,
        args = (permission, Presentation, 'provideView', for_, name,
                type, factory, layer, provides),
        )
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = (type.__module__+'.'+type.__name__, type)
               )
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = (provides.__module__+'.'+provides.__name__, type)
               )

    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = (for_.__module__+'.'+for_.getName(),
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
        args = (Presentation, 'setDefaultViewName', for_, type, name),
        )
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = (type.__module__+'.'+type.getName(), type)
        )

    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = (for_.__module__+'.'+for_.getName(), for_)
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

def layer(_context, name):

    _context.action(
        discriminator = ('layer', name),
        callable = handler,
        args = (Presentation, 'defineLayer', name)
        )

def skin(_context, name, layers):
    if ',' in layers:
        raise TypeError("Commas are not allowed in layer names.")

    _context.action(
        discriminator = ('skin', name),
        callable = handler,
        args = (Presentation, 'defineSkin', name, layers)
        )

def defaultSkin(_context, name):
    _context.action(
        discriminator = 'defaultSkin',
        callable = handler,
        args = (Presentation, 'setDefaultSkin', name)
        )

def usage(_context, name):

    _context.action(
        discriminator = ('usage', name),
        callable = handler,
        args = (Presentation, 'defineUsage', name)
        )