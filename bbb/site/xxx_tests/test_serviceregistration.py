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
"""Service Registration tests.

$Id$
"""

from unittest import TestCase, main, makeSuite

from zope.interface import Interface, implements

from zope.app.traversing.api import traverse, getPath
from zope.app.site.service import ServiceRegistration
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.component.service import defineService
from zope.app.site.interfaces import IBindingAware
from zope.app.registration.interfaces import ActiveStatus
from zope.app.registration.interfaces import RegisteredStatus
from zope.app.registration.interfaces import IRegistered
from zope.app.site.interfaces import ISimpleService

from zope.app.dependable.interfaces import IDependable, DependencyError

class ITestService(Interface):
    pass

class TestServiceBase(object):
    __name__ = __parent__ = None
    implements(ITestService, IBindingAware, IDependable)
    
    _bound = _unbound = ()

    def bound(self, name):
        self._bound += (name, )

    def unbound(self, name):
        self._unbound += (name, )

    _dependents = ()

    def addDependent(self, location):
        self._dependents = tuple(
            [d for d in self._dependents if d != location]
            +
            [location]
            )

    def removeDependent(self, location):
        self._dependents = tuple(
            [d for d in self._dependents if d != location]
            )

    def dependents(self):
        return self._dependents

class TestService(TestServiceBase):
    implements(ISimpleService)

class Event(object):

    def __init__(self, object):
        self.object = object

class Test(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self, site=True)

        defineService('test_service', ITestService)

        default = traverse(self.rootFolder,
                           '++etc++site/default')
        self.__default = default

        default['c'] = TestService()

        registration = ServiceRegistration(
            'test_service', default['c'])

        self.__c = traverse(default, 'c')
        self.__cm = default.getRegistrationManager()

        self.__registration_name = self.__cm.addRegistration(registration)

        self.__config = traverse(self.__cm, self.__registration_name)
        self.__configpath = getPath(self.__config)

    def test_handleActivated(self):
        old = self.__c._bound
        event = Event(self.__config)
        from zope.app.site.service import handleActivated
        handleActivated(event)
        self.assertEqual(self.__c._bound, old+('test_service',))

    def test_deactivated(self):
        old = self.__c._unbound
        event = Event(self.__config)
        from zope.app.site.service import handleDeactivated
        handleDeactivated(event)
        self.assertEqual(self.__c._unbound, old+('test_service',))

    def test_getInterface(self):
        self.assertEquals(self.__config.getInterface(), ITestService)

    # The following tests check the same things as
    # zope.app.services.tests.testregistrations, but in a different way

    def test_getComponent(self):
        self.assertEqual(self.__config.component, self.__c)

    def test_not_a_local_service(self):
        defineService('test_service_2', ITestService)
        self.__default['c2'] = TestServiceBase()

        self.assertRaises(
            TypeError,
            ServiceRegistration,
            'test_service',
            self.__default['c2'],
            self.__default
            )


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
