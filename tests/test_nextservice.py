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
"""
$Id$
"""

from unittest import TestCase, main, makeSuite
from zope.app.component.hooks import getServiceManager_hook
from zope.app.component.nextservice import getNextServiceManager
from zope.app.site.interfaces import IPossibleSite, ISite
from zope.app.traversing import IContainmentRoot
from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IServiceService
from zope.component.service import serviceManager
from zope.interface import implements, directlyProvides, directlyProvidedBy


class ServiceManager:
    implements(IServiceService)

class Folder:
    implements(IPossibleSite)

    sm = None

    def getSiteManager(self, default=None):
        return self.sm

    def setSiteManager(self, sm):
        self.sm = sm
        sm.__parent__ = self
        directlyProvides(self, ISite, directlyProvidedBy(self))

class Root(Folder):
    implements(IContainmentRoot)


def Wrapper(ob, container):
    ob.__parent__ = container
    return ob

class Test(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        root = Root()

        f1 = Wrapper(Folder(), root)
        sm1 = ServiceManager()
        f1.setSiteManager(sm1)

        f2 = Wrapper(Folder(), f1)
        sm2 = ServiceManager()
        f2.setSiteManager(sm2)

        self.root = root
        self.f1 = f1
        self.f2 = f2
        self.sm1 = sm1
        self.sm2 = sm2

    def test_getServiceManager(self):

        self.assertEqual(getServiceManager_hook(self.root), serviceManager)
        self.assertEqual(getServiceManager_hook(self.f1), self.sm1)
        self.assertEqual(getServiceManager_hook(self.f2), self.sm2)

    def test_getNextServiceManager(self):

        self.assertRaises(ComponentLookupError,
                          getNextServiceManager, self.root)

        self.assertEqual(getNextServiceManager(Wrapper(self.sm1, self.f1)),
                         serviceManager)
        self.assertEqual(getNextServiceManager(Wrapper(self.sm2, self.f2)),
                         self.sm1)

    def test_getNextServiceManager_fails_w_bad_root(self):
        root = Folder()
        f1 = Wrapper(Folder(), root)
        sm1 = ServiceManager()
        f1.setSiteManager(sm1)
        self.assertRaises(TypeError,
                          getNextServiceManager, Wrapper(sm1, f1)
                          )

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
