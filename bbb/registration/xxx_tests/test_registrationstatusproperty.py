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
"""Registration Status Property Tests

$Id$
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.component.interfaces import IServiceService
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.registration.tests.registrationstack import TestingRegistration
from zope.app.registration.tests.registrationstack import \
     TestingRegistrationStack
from zope.app.registration.interfaces import RegisteredStatus
from zope.app.registration.interfaces import UnregisteredStatus
from zope.app.registration.interfaces import ActiveStatus
from zope.app.registration.interfaces import NoLocalServiceError
from zope.component.exceptions import ComponentLookupError
from zope.interface import implements
from zope.app.container.contained import contained

class TestingRegistration(TestingRegistration):
    serviceType = "Services"
    service_type = "Test"

class PassiveRegistration(TestingRegistration):
    serviceType = "NoSuchService"

class UtilityRegistration(TestingRegistration):
    serviceType = "Utilities"


class TestingServiceManager(object):

    implements(IServiceService) # I lied

    registry = None

    def getService(self, name):
        if name in ("Services", "Utilities"):
            return self
        raise ComponentLookupError("Wrong service name", name)

    def queryLocalService(self, name, default=None):
        if name == "Services":
            return self
        else:
            return default

    def queryRegistrationsFor(self, registration, default=None):
        if registration.service_type != "Test":
            raise ValueError("Bad service type", registration.service_type)
        return self.registry

    def createRegistrationsFor(self, registration):
        if registration.service_type != "Test":
            raise ValueError("Bad service type", registration.service_type)
        self.registry = TestingRegistrationStack()
        return self.registry


class Test(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self, folders=True)
        self.__sm = TestingServiceManager()
        self.rootFolder.setSiteManager(self.__sm)

    def test_property(self):

        configa = contained(TestingRegistration('a'), self.rootFolder)
        self.assertEqual(configa.status, UnregisteredStatus)

        configa.status = RegisteredStatus

        data = [(int(info['active']), info['registration'].id)
                for info in self.__sm.registry.info()]
        self.assertEqual(data, [(0, 'a')])
        self.assertEqual(configa.status, RegisteredStatus)

        configa.status = ActiveStatus
        data = [(info['active'], info['registration'].id)
                for info in self.__sm.registry.info()]
        self.assertEqual(data, [(1, 'a')])
        self.assertEqual(configa.status, ActiveStatus)

        configb = contained(TestingRegistration('b'), self.rootFolder)
        data = [(info['active'], info['registration'].id)
                for info in self.__sm.registry.info()]
        self.assertEqual(data, [(1, 'a',)])
        self.assertEqual(configb.status, UnregisteredStatus)

        configb.status = RegisteredStatus
        data = [(info['active'], info['registration'].id)
                for info in self.__sm.registry.info()]
        self.assertEqual(data, [(1, 'a'), (0, 'b')])
        self.assertEqual(configb.status, RegisteredStatus)

        configc = contained(TestingRegistration('c'), self.rootFolder)
        self.assertEqual(configc.status, UnregisteredStatus)
        self.assertEqual(data, [(1, 'a'), (0, 'b')])

        configc.status = RegisteredStatus
        data = [(info['active'], info['registration'].id)
                for info in self.__sm.registry.info()]
        self.assertEqual(data, [(1, 'a'), (0, 'b'), (0, 'c')])
        self.assertEqual(configc.status, RegisteredStatus)

        configc.status = ActiveStatus
        data = [(info['active'], info['registration'].id)
                for info in self.__sm.registry.info()]
        self.assertEqual(data, [(1, 'c'), (0, 'a'), (0, 'b')])
        self.assertEqual(configc.status, ActiveStatus)

        configc.status = UnregisteredStatus
        data = [(int(info['active']), info['registration'].id)
                for info in self.__sm.registry.info()]
        self.assertEqual(data, [(1, 'a'), (0, 'b')])
        self.assertEqual(configc.status, UnregisteredStatus)
        self.assertEqual(configb.status, RegisteredStatus)
        self.assertEqual(configa.status, ActiveStatus)

    def test_passive(self):
        # scenario:
        #   1. create and configure an SQLConnectionService
        #   2. create and configure a database adapter&connection
        #   3. disable SQLConnectionService
        # now the ConnectionRegistration.status cannot access the
        # SQLConnectionService

        configa = contained(PassiveRegistration('a'), self.rootFolder)
        self.assertEqual(configa.status, UnregisteredStatus)

        try:
            configa.status = RegisteredStatus
        except NoLocalServiceError:
            self.assertEqual(configa.status, UnregisteredStatus)
        else:
            self.fail("should complain about missing service")

        try:
            configa.status = ActiveStatus
        except NoLocalServiceError:
            self.assertEqual(configa.status, UnregisteredStatus)
        else:
            self.fail("should complain about missing service")


        # we should also get an error if there *is a matching service,
        # not it is non-local

        configa = contained(UtilityRegistration('a'), self.rootFolder)
        self.assertEqual(configa.status, UnregisteredStatus)

        try:
            configa.status = RegisteredStatus
        except NoLocalServiceError:
            self.assertEqual(configa.status, UnregisteredStatus)
        else:
            self.fail("should complain about missing service")

        try:
            configa.status = ActiveStatus
        except NoLocalServiceError:
            self.assertEqual(configa.status, UnregisteredStatus)
        else:
            self.fail("should complain about missing service")


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
