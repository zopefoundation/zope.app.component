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
""" Register class directive.

$Id: contentdirective.py,v 1.3 2003/07/28 22:21:05 jim Exp $
"""
from zope.interface import classProvides
from types import ModuleType
from zope.interface import implements, classImplements
from zope.component import getService
from zope.app.services.servicenames import Interfaces, Factories
from zope.configuration.exceptions import ConfigurationError
from zope.configuration.action import Action
from zope.app.component.classfactory import ClassFactory
from zope.app.component.metaconfigure import resolveInterface
from zope.app.security.protectclass \
    import protectLikeUnto, protectName, protectSetAttribute
from zope.app.security.registries.permissionregistry import permissionRegistry
from zope.security.proxy import ProxyFactory
from zope.security.checker import NamesChecker, CheckerPublic
from zope.schema.interfaces import IField

PublicPermission = 'zope.Public'

class ProtectionDeclarationException(Exception):
    """Security-protection-specific exceptions."""
    pass

def handler(serviceName, methodName, *args, **kwargs):
    method=getattr(getService(None, serviceName), methodName)
    method(*args, **kwargs)

def assertPermission(permission=None, *args, **kw):
    """Check if permission is defined"""
    if permission is not None:
        permissionRegistry.ensurePermissionDefined(permission)

class ContentDirective:

    def __init__(self, _context, class_):
        self.__id = class_
        self.__class = _context.resolve(class_)
        if isinstance(self.__class, ModuleType):
            raise ConfigurationError('Content class attribute must be a class')
        # not used yet
        #self.__name = class_
        #self.__normalized_name = _context.getNormalizedName(class_)
        self.__context = _context

    def implements(self, _context, interface):
        r = []
        for interface in interface.strip().split():

            resolved_interface = resolveInterface(_context, interface)
            r += [
                Action(
                    discriminator = (
                        'ContentDirective', self.__class, object()),
                    callable = classImplements,
                    args = (self.__class, resolved_interface),
                    ),
                Action(
                   discriminator = None,
                   callable = handler,
                   args = (Interfaces, 'provideInterface',
                           resolved_interface.__module__+
                           '.'+
                           resolved_interface.__name__,
                           resolved_interface)
                   )
                ]
        return r

    def require(self, _context,
                permission=None, attributes=None, interface=None,
                like_class=None, set_attributes=None, set_schema=None):
        """Require a the permission to access a specific aspect"""

        if like_class:
            r = self.__mimic(_context, like_class)
        else:
            r = []

        if not (interface or attributes or set_attributes or set_schema):
            if r:
                return r
            raise ConfigurationError("Nothing required")

        if not permission:
            raise ConfigurationError("No permission specified")


        if interface:
            for i in interface.strip().split():
                self.__protectByInterface(i, permission, r)
        if attributes:
            self.__protectNames(attributes, permission, r)
        if set_attributes:
            self.__protectSetAttributes(set_attributes, permission, r)
        if set_schema:
            for s in set_schema.strip().split():
                self.__protectSetSchema(s, permission, r)


        return r

    def __mimic(self, _context, class_):
        """Base security requirements on those of the given class"""
        class_to_mimic = _context.resolve(class_)
        return [
            Action(discriminator=('mimic', self.__class, object()),
                   callable=protectLikeUnto,
                   args=(self.__class, class_to_mimic),
                   )
            ]

    def allow(self, _context, attributes=None, interface=None):
        """Like require, but with permission_id zope.Public"""
        return self.require(_context, PublicPermission, attributes, interface)



    def __protectByInterface(self, interface, permission_id, r):
        "Set a permission on names in an interface."
        interface = resolveInterface(self.__context, interface)
        for n, d in interface.namesAndDescriptions(1):
            self.__protectName(n, permission_id, r)
        r.append(
            Action(
               discriminator = None,
               callable = handler,
               args = (Interfaces, 'provideInterface',
                       interface.__module__+ '.'+ interface.__name__,
                       interface)
               )
            )

    def __protectName(self, name, permission_id, r):
        "Set a permission on a particular name."
        r.append((
            ('protectName', self.__class, name),
            protectName, (self.__class, name, permission_id)))

    def __protectNames(self, names, permission_id, r):
        "Set a permission on a bunch of names."
        for name in names.split():
            self.__protectName(name.strip(), permission_id, r)

    def __protectSetAttributes(self, names, permission_id, r):
        "Set a permission on a bunch of names."
        for name in names.split():
            r.append((
                ('protectSetAttribute', self.__class, name),
                protectSetAttribute, (self.__class, name, permission_id)))

    def __protectSetSchema(self, schema, permission_id, r):
        "Set a permission on a bunch of names."
        schema = resolveInterface(self.__context, schema)
        for name in schema:
            field = schema[name]
            if IField.isImplementedBy(field) and not field.readonly:
                r.append((
                    ('protectSetAttribute', self.__class, name),
                    protectSetAttribute, (self.__class, name, permission_id)))

        r.append(
            Action(
               discriminator = None,
               callable = handler,
               args = (Interfaces, 'provideInterface',
                       schema.__module__+ '.'+ schema.__name__,
                       schema)
               )
            )


    def __call__(self):
        "Handle empty/simple declaration."
        return ()


    def factory(self, _context,
                permission=None, title="", id=None, description=''):
        """Register a zmi factory for this class"""

        id = id or self.__id

        # note factories are all in one pile, services and content,
        # so addable names must also act as if they were all in the
        # same namespace, despite the service/content division
        return [
            Action(
                discriminator = ('FactoryFromClass', id),
                callable = provideClass,
                args = (id, self.__class,
                        permission, title, description)
                )
            ]

def provideClass(id, _class, permission=None,
                 title='', description=''):
    """Provide simple class setup

    - create a component

    - set component permission
    """

    assertPermission(permission)
    factory = ClassFactory(_class)

    if permission == PublicPermission:
        permission = CheckerPublic

    if permission:
        # XXX should getInterfaces be public, as below?
        factory = ProxyFactory(factory,
                               NamesChecker(('getInterfaces',),
                                            __call__=permission))

    getService(None, Factories).provideFactory(id, factory)
