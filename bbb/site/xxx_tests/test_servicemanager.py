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
"""Service Manager Tests

$Id$
"""
from unittest import TestCase, TestLoader, TextTestRunner

from zope.app import zapi
from zope.app.tests import setup
from zope.interface import Interface, implements
from zope.app.site.service import ServiceManager, ServiceRegistration
from zope.component import getService, getServices, getGlobalServices
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.traversing.api import traverse
from zope.app.registration.interfaces import UnregisteredStatus
from zope.app.registration.interfaces import ActiveStatus
from zope.app.registration.interfaces import RegisteredStatus
from zope.component.service import serviceManager
from zope.app.annotation.interfaces import IAttributeAnnotatable

class ITestService(Interface):
    pass

class TestService(object):
    implements(ITestService, IAttributeAnnotatable)

class ServiceManagerTests(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self, site=True)
        serviceManager.defineService('test_service', ITestService)

    def testGetService(self):
        sm = traverse(self.rootFolder, '++etc++site')
        default = traverse(sm, 'default')

        ts = TestService()
        default['test_service1'] = ts
        registration = ServiceRegistration('test_service',
                                           default['test_service1'])

        rm = default.getRegistrationManager()
        name = rm.addRegistration(registration)
        traverse(rm, name).status = ActiveStatus

        testOb = getService('test_service', self.rootFolder)
        self.assertEqual(testOb.__parent__.__parent__.__parent__,
                         self.rootFolder)
        self.assertEqual(testOb, ts)
        # used by one of the callers
        return name

    def test_queryLocalService(self):
        sm = traverse(self.rootFolder, '++etc++site')

        # Test no service case
        self.assertEqual(sm.queryLocalService('test_service'), None)
        self.assertEqual(sm.queryLocalService('test_service', 42), 42)

        # Test Services special case
        self.assertEqual(sm.queryLocalService('Services', 42), sm)

        # Test found local
        default = traverse(sm, 'default')
        ts = TestService()
        default['test_service1'] = ts
        registration = ServiceRegistration('test_service',
                                           default['test_service1'])
        rm = default.getRegistrationManager()
        name = rm.addRegistration(registration)
        traverse(rm, name).status = ActiveStatus

        testOb = sm.queryLocalService('test_service')
        self.assertEqual(testOb.__parent__.__parent__.__parent__,
                         self.rootFolder)
        self.assertEqual(testOb, ts)


    def test_get(self):
        sm = traverse(self.rootFolder, '++etc++site')
        default = sm.get('default')
        self.assertEqual(default, sm['default'])
        self.assertEqual(sm.get('spam'), None)

    def testAddService(self):
        sm = traverse(self.rootFolder, '++etc++site')
        default = traverse(sm, 'default')

        ts1 = TestService()
        default['test_service1'] = ts1
        registration = ServiceRegistration('test_service',
                                           default['test_service1'])
        rm = default.getRegistrationManager()
        name = rm.addRegistration(registration)
        traverse(rm, name).status = ActiveStatus

        ts2 = TestService()
        default['test_service2'] = ts2
        registration = ServiceRegistration('test_service',
                                           default['test_service2'])
        name = rm.addRegistration(registration)
        traverse(rm, name).status = RegisteredStatus

        testOb = getService('test_service', self.rootFolder)
        self.assertEqual(testOb, ts1)


    def testUnbindService(self):

        root_ts = TestService()
        gsm = getGlobalServices()
        gsm.provideService('test_service', root_ts)

        name = self.testGetService() # set up localservice

        sm = traverse(self.rootFolder, '++etc++site')
        cm = traverse(sm, 'default').getRegistrationManager()
        traverse(cm, name).status = UnregisteredStatus

        self.assertEqual(getService('test_service', self.rootFolder), root_ts)

    def testContextServiceLookup(self):
        self.testGetService() # set up localservice
        sm = getServices(self.rootFolder)
        self.assertEqual(getService('test_service', self.folder1_1),
                         sm['default']['test_service1'])

    def testContextServiceLookupWithMultipleServiceManagers(self):
        self.testGetService() # set up root localservice
        sm = getServices(self.rootFolder)

        sm2 = self.makeSite('folder1')

        self.assertEqual(getService('test_service', self.folder1),
                         sm['default']['test_service1'])

    def testComponentArchitectureServiceLookup(self):
        self.makeSite()
        self.makeSite('folder1')

        ts = TestService()

        globsm = getGlobalServices()
        globsm.provideService('test_service', ts)

        service = getService('test_service', self.folder1)
        self.assertEqual(service, ts)

    def test_site_manager_connections(self):
        root = self.rootFolder
        mr = root.getSiteManager()
        m1 = setup.createServiceManager(zapi.traverse(root, 'folder1')) 
        m2 = setup.createServiceManager(zapi.traverse(root, 'folder2'))
        m111 = setup.createServiceManager(
            zapi.traverse(root, 'folder1/folder1_1/folder1_1_1'))
        self.assertEqual(m1.next, mr)
        self.assertEqual(m2.next, mr)
        self.assertEqual(m111.next, m1)
        self.assertEqual(mr.subSites, (m1, m2))
        self.assertEqual(m1.subSites, (m111, ))

        # Now insert a site and make sure everything is still right:
        m11 = setup.createServiceManager(
            zapi.traverse(root, 'folder1/folder1_1'))
        self.assertEqual(m11.next, m1)
        self.assertEqual(m111.next, m11)
        self.assertEqual(m1.subSites, (m11, ))
        self.assertEqual(m11.subSites, (m111, ))

        


def test_suite():
    loader=TestLoader()
    return loader.loadTestsFromTestCase(ServiceManagerTests)

if __name__=='__main__':
    TextTestRunner().run(test_suite())
