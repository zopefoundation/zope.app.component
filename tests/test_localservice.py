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
"""Test local service code

$Id$
"""
import unittest
from zope.component import getGlobalServices
from zope.app.component.hooks import getServices_hook
from zope.app.component.localservice import serviceServiceAdapter
from zope.app.site.interfaces import IPossibleSite, ISite, ISiteManager
from zope.app.traversing.interfaces import IContainmentRoot
from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IServiceService
from zope.component.service import serviceManager
from zope.interface import implements, directlyProvides, directlyProvidedBy
from zope.interface.verify import verifyObject
from zope.app.tests.setup import placelessSetUp, placelessTearDown
from zope.app.tests import ztapi
from zope.app.component.hooks import setSite, getSite

class ServiceManager(object):
    implements(ISiteManager)

    def __init__(self):
        self.dummy_service = object()

    def getService(self, name):
        if name == 'dummy':
            return self.dummy_service
        raise ComponentLookupError(name)

class Folder(object):
    implements(IPossibleSite)

    sm = None

    def getSiteManager(self, default=None):
        return self.sm

    def setSiteManager(self, sm):
        self.sm = sm
        sm.__parent__ = self
        directlyProvides(self, ISite, directlyProvidedBy(self))

class Package(object):
    pass

class Root(Folder):
    implements(IContainmentRoot, ISite)
    def getSiteManager(self):
        return getGlobalServices()

class ServiceServiceStub(object):
    implements(IServiceService)


def Wrapper(ob, container):
    ob.__parent__ = container
    return ob

class Test(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        placelessSetUp()
        root = Root()

        f1 = Wrapper(Folder(), root)
        sm1 = ServiceManager()
        f1.setSiteManager(sm1)
        p1 = Wrapper(Package(), sm1)

        f2 = Wrapper(Folder(), f1)
        sm2 = ServiceManager()
        f2.setSiteManager(sm2)
        p2 = Wrapper(Package(), sm2)

        sm1.next = serviceManager
        sm2.next = sm1

        self.root = root
        self.f1 = f1
        self.f2 = f2
        self.sm1 = sm1
        self.sm2 = sm2
        self.p1 = p1
        self.p2 = p2
        self.unparented_folder = Folder()
        self.unrooted_subfolder = Wrapper(Folder(), self.unparented_folder)

        ztapi.provideAdapter(None, IServiceService, serviceServiceAdapter)

    def tearDown(self):
        setSite()
        placelessTearDown()

    def test_getServices(self):
        self.assertEqual(getServices_hook(None), serviceManager)
        self.assertEqual(getServices_hook(self.root), serviceManager)
        self.assertEqual(getServices_hook(self.f1), self.sm1)
        self.assertEqual(getServices_hook(self.f2), self.sm2)
        setSite(self.f2)
        self.assertEqual(getServices_hook(None), self.sm2)

    def test_queryNextService(self):
        from zope.app.component.localservice import queryNextService
        self.assert_(queryNextService(self.sm2, 'dummy') is
                     self.sm1.dummy_service)
        self.assert_(queryNextService(self.p2, 'dummy') is
                     self.sm1.dummy_service)
        marker = object()
        self.assert_(queryNextService(self.p1, 'dummy', marker) is marker)

    def test_getNextService(self):
        from zope.app.component.localservice import getNextService
        self.assert_(getNextService(self.sm2, 'dummy') is
                     self.sm1.dummy_service)
        self.assert_(getNextService(self.p2, 'dummy') is
                     self.sm1.dummy_service)
        self.assertRaises(ComponentLookupError,
                          getNextService, self.p1, 'dummy')


    def test_queryNextServices(self):
        from zope.app.component.localservice import queryNextServices
        marker = object()
        self.assert_(queryNextServices(self.root, marker) is marker)
        self.assert_(queryNextServices(self.f1, marker) is marker)
        self.assert_(queryNextServices(self.f2, marker) is marker)
        self.assertEqual(queryNextServices(self.sm1), serviceManager)
        self.assertEqual(queryNextServices(self.sm2), self.sm1)
        self.assertEqual(queryNextServices(self.p1), serviceManager)
        self.assertEqual(queryNextServices(self.p2), self.sm1)

        self.assert_(queryNextServices(self.unparented_folder, marker)
                     is marker)
        self.assert_(queryNextServices(self.unrooted_subfolder, marker)
                     is marker)

    def test_getNextServices(self):
        from zope.app.component.localservice import getNextServices
        self.assertRaises(ComponentLookupError,
                          getNextServices, self.root)
        self.assertRaises(ComponentLookupError,
                          getNextServices, self.f1)
        self.assertRaises(ComponentLookupError,
                          getNextServices, self.f2)
        self.assertEqual(getNextServices(self.sm1), serviceManager)
        self.assertEqual(getNextServices(self.sm2), self.sm1)
        self.assertEqual(getNextServices(self.p1), serviceManager)
        self.assertEqual(getNextServices(self.p2), self.sm1)

        self.assertRaises(ComponentLookupError,
                          getNextServices, self.unparented_folder)
        self.assertRaises(ComponentLookupError,
                          getNextServices, self.unrooted_subfolder)

    def test_getNextServices_security(self):
        from zope.app.component.localservice import getNextServices
        from zope.security.checker import ProxyFactory, NamesChecker
        sm = ProxyFactory(self.sm1, NamesChecker(('next',)))
        # Check that serviceManager is not proxied
        self.assert_(getNextServices(sm) is serviceManager)

    def test_queryLocalServices(self):
        from zope.app.component.localservice import queryLocalServices
        marker = object()
        self.assert_(queryLocalServices(self.root, marker) is marker)
        self.assert_(queryLocalServices(self.f1, marker) is marker)
        self.assert_(queryLocalServices(self.f2, marker) is marker)
        self.assertEqual(queryLocalServices(self.sm1), self.sm1)
        self.assertEqual(queryLocalServices(self.sm2), self.sm2)
        self.assertEqual(queryLocalServices(self.p1), self.sm1)
        self.assertEqual(queryLocalServices(self.p2), self.sm2)

        self.assert_(queryLocalServices(self.unparented_folder, marker)
                     is marker)
        self.assert_(queryLocalServices(self.unrooted_subfolder, marker)
                     is marker)

    def test_getLocalServices(self):
        from zope.app.component.localservice import getLocalServices
        self.assertRaises(ComponentLookupError,
                          getLocalServices, self.root)
        self.assertRaises(ComponentLookupError,
                          getLocalServices, self.f1)
        self.assertRaises(ComponentLookupError,
                          getLocalServices, self.f2)
        self.assertEqual(getLocalServices(self.sm1), self.sm1)
        self.assertEqual(getLocalServices(self.sm2), self.sm2)
        self.assertEqual(getLocalServices(self.p1), self.sm1)
        self.assertEqual(getLocalServices(self.p2), self.sm2)

        unparented_folder = Folder()
        self.assertRaises(ComponentLookupError,
                          getLocalServices, unparented_folder)
        unrooted_subfolder = Wrapper(Folder(), unparented_folder)
        self.assertRaises(ComponentLookupError,
                          getLocalServices, unrooted_subfolder)

    def test_serviceServiceAdapter(self):
        from zope.app.component.localservice import serviceServiceAdapter

        # If it is a site, return the service service.
        ss = ServiceServiceStub()
        site = Folder()
        site.setSiteManager(ss)
        self.assertEqual(serviceServiceAdapter(site), ss)

        # If it is locatable (has __parent__), "acquire" the site
        # and return the service service
        ob = Folder()
        ob.__parent__ = site
        self.assertEqual(serviceServiceAdapter(ob), ss)
        ob2 = Folder()
        ob2.__parent__ = ob
        self.assertEqual(serviceServiceAdapter(ob2), ss)

        # If it does we are unable to find a service service, raise
        # ComponentLookupError
        orphan = Folder()
        self.assertRaises(ComponentLookupError, serviceServiceAdapter, orphan)

    def test_setThreadSite_clearThreadSite(self):
        from zope.app.component.localservice import threadSiteSubscriber
        from zope.app.component.localservice import clearSite
        from zope.app.publication.zopepublication import BeforeTraverseEvent

        self.assertEqual(getSite(), None)

        # A non-site is traversed
        ob = object()
        request = object()
        ev = BeforeTraverseEvent(ob, request)
        threadSiteSubscriber(ev)

        self.assertEqual(getSite(), None)

        # A site is traversed
        ss = ServiceServiceStub()
        site = Folder()
        site.setSiteManager(ss)

        ev = BeforeTraverseEvent(site, request)
        threadSiteSubscriber(ev)

        self.assertEqual(getSite(), site)

        clearSite()

        self.assertEqual(getSite(), None)


def test_suite():
    return unittest.makeSuite(Test)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
