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
"""Component registration support

$Id$
"""

from zope.app.event import objectevent
from zope.interface import implements
import zope.app.component.interfaces.registration
import zope.deferredimport

zope.deferredimport.deprecatedFrom(
    """The old registration APIs, are deprecated and will go away in Zope 3.5

    See the newer component-registration APIs in
    zope.component.interfaces.IComponentRegistry.
    """,
    "zope.app.component.back35",
    'RegistrationStatusProperty',
    'SimpleRegistration',
    'ComponentRegistration',
    'Registered',
    'RegistrationManager',
    'RegisterableContainer',
    'RegistrationManagerNamespace',
    )

class RegistrationEvent(objectevent.ObjectEvent):
    """An event that is created when a registration-related activity occurred.
    """
    implements(zope.app.component.interfaces.registration.IRegistrationEvent)

class RegistrationActivatedEvent(RegistrationEvent):
    """An event that is created when a registration is activated."""
    implements(
        zope.app.component.interfaces.registration.IRegistrationActivatedEvent,
        )

class RegistrationDeactivatedEvent(RegistrationEvent):
    """An event that is created when a registration is deactivated."""
    implements(
      zope.app.component.interfaces.registration.IRegistrationDeactivatedEvent,
      )



