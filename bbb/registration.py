##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Registration BBB components

$Id$
"""
__docformat__ = "reStructuredText"
from zope.interface import implements

from zope.app import zapi
from zope.app.container.contained import Contained

import interfaces


class RegistrationStack(Contained):
    """Registration registry implemention

       A registration stack provides support for a collection of
       registrations such that, at any time, at most one is active.  The
       "stack" aspect of the api is designed to support "uninstallation",
       as will be described below.
       """
    implements(interfaces.IRegistrationStack)

    def __init__(self, container):
        self.__parent__ = container
        self.sitemanager = zapi.getSiteManager(container)

    def register(self, registration):
        self.sitemanager.register(registration)
        self._activate(registration)

    def unregister(self, registration):
        self.sitemanager.register(registration)
        self._deactivate(registration)

    def registered(self, registration):
        self.sitemanager.registered(registration)

    def _activate(self, registration):
        zope.event.notify(RegistrationActivatedEvent(registration))
        registration.activated()

    def _deactivate(self, registration):
        zope.event.notify(RegistrationDeactivatedEvent(registration))
        registration.deactivated()

    def activate(self, registration):
        self.sitemanager.register(registration)
        self._activate(registration)


    def deactivate(self, registration):
        self.sitemanager.register(registration)
        self._deactivate(registration)

    def active(self):
        return True

    def __nonzero__(self):
        # XXX: Needs to be done
        return bool(self.data)

    def info(self):
        # XXX: Needs to be done
        result = [{'active': False,
                   'registration': registration,
                  }
                  for registration in data
                 ]

        if result:
            result[0]['active'] = True

        return [r for r in result if r['registration'] is not None]

    def data(self):
        # XXX: Note done
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


class BBBRegistry(object):

    def queryRegistrationsFor(self, cfg, default=None):
        return RegistrationStack(self, name)

    def createRegistrationsFor(self, cfg):
        # Ignore
        pass
    

class BBBRegisterableContainer(object):

    def getRegistrationManager(self):
        return self.registrationManager

    def findModule(self, name):
        from zope.app.module import findModule
        return findModule(name)

    def resolve(self, name):
        from zope.app.module import resolve
        return resolve(name)
        


class BBBRegistered(object):

    def addUsage(self, location):
        # Ignore in the hope that noone uses this
        pass

    def removeUsage(self, location):
        # Ignore in the hope that noone uses this
        pass

    def usages(self):
        return [zapi.getPath(reg.component)
                for reg in self.registrations]
