##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Interfaces pertaining to local utilities.

$Id$
"""
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.registration.interfaces import IComponentRegistration
from zope.app.registration.interfaces import IRegisterable
from zope.app.registration.interfaces import IRegistry
from zope.app.registration.interfaces import ComponentPath
from zope.schema import TextLine, Choice
import zope.component.interfaces

class ILocalUtilityService(
        zope.component.interfaces.IUtilityService,
        IRegistry,
        ):
    """Local Utility Service."""

class IUtilityRegistration(IComponentRegistration):
    """Utility registration object.

    This is keyed off name (which may be empty) and interface. It inherits the
    `component` property.
    """

    name = TextLine(
        title=_("Register As"),
        description=_("The name that is registered"),
        readonly=True,
        required=True,
        )

    interface = Choice(
        title=_("Provided interface"),
        description=_("The interface provided by the utility"),
        vocabulary="Utility Component Interfaces",
        readonly=True,
        required=True,
        )


class ILocalUtility(IRegisterable):
    """Local utility marker.

    A marker interface that indicates that a component can be used as
    a local utility.

    Utilities should usually also declare they implement
    IAttributeAnnotatable, so that the standard adapter to
    IRegistered can be used; otherwise, they must provide
    another way to be adaptable to IRegistered.
    """
