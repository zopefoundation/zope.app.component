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
$Id: test_nextservice.py,v 1.4 2003/03/11 21:08:40 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.component.hooks import getServiceManager_hook
from zope.app.component.nextservice import getNextServiceManager
from zope.app.interfaces.services.service import IServiceManagerContainer
from zope.app.traversing import IContainmentRoot
from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IServiceService
from zope.component.service import serviceManager
from zope.interface import Interface
from zope.proxy.context import Wrapper


class ServiceManager:
    __implements__ =  IServiceService

class Folder:
    __implements__ =  IServiceManagerContainer

    sm = None

    def getServiceManager(self, default=None):
        return self.sm

    def hasServiceManager(self):
        return self.sm

    def setServiceManager(self, sm):
        self.sm = sm

class Root(Folder):
    __implements__ =  IServiceManagerContainer, IContainmentRoot

root = Root()

f1 = Wrapper(Folder(), root)
sm1 = ServiceManager()
f1.setServiceManager(sm1)

f2 = Wrapper(Folder(), f1)
sm2 = ServiceManager()
f2.setServiceManager(sm2)



class Test(TestCase):

    def test_getServiceManager(self):

        self.assertEqual(getServiceManager_hook(root), serviceManager)
        self.assertEqual(getServiceManager_hook(f1), sm1)
        self.assertEqual(getServiceManager_hook(f2), sm2)

    def test_getNextServiceManager(self):

        self.assertRaises(ComponentLookupError,
                          getNextServiceManager, root)

        self.assertEqual(getNextServiceManager(Wrapper(sm1, f1)),
                         serviceManager)
        self.assertEqual(getNextServiceManager(Wrapper(sm2, f2)), sm1)

    def test_getNextServiceManager_fails_w_bad_root(self):
        root = Folder()
        f1 = Wrapper(Folder(), root)
        sm1 = ServiceManager()
        f1.setServiceManager(sm1)
        self.assertRaises(TypeError,
                          getNextServiceManager, Wrapper(sm1, f1)
                          )

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
