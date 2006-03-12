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

from zope import interface, schema
import zope.schema.interfaces
import zope.app.event.interfaces

import zope.deferredimport

zope.deferredimport.deprecatedFrom(
    "Local registration is now much simpler.  The old baroque APIs "
    "will go away in Zope 3.5.  See the new component-registration APIs "
    "defined in zope.component, especially IComponentRegistry.",
    'zope.app.component.back35',
    'IRegistration',
    'InactiveStatus',
    'ActiveStatus',
    'IComponentRegistration',
    'IRegistry',
    'ILocatedRegistry',
    'IRegistrationManager',
    'IRegistrationManagerContained',
    'IRegisterableContainer',
    'IRegisterable',
    'IRegisterableContainerContaining',
    'IRegistered',
    )


class IRegistrationEvent(zope.app.event.interfaces.IObjectEvent):
    """An event that involves a registration"""

class IRegistrationActivatedEvent(IRegistrationEvent):
    """This event is fired, when a component's registration is activated."""

class IRegistrationDeactivatedEvent(IRegistrationEvent):
    """This event is fired, when a component's registration is deactivated."""


class IComponent(zope.schema.interfaces.IField):
    """A component path

    This is just the interface for the ComponentPath field below.  We'll use
    this as the basis for looking up an appropriate widget.
    """

class Component(schema.Field):
    """A component path

    Values of the field are absolute unicode path strings that can be
    traversed to get an object.
    """
    interface.implements(IComponent)

