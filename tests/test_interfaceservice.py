##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
import unittest

from zope.interface import Interface

from zope.app.interfaces.component import IGlobalInterfaceService
from zope.app.component.globalinterfaceservice import InterfaceService
from zope.app.component.tests.absIInterfaceService \
     import IInterfaceServiceTests

from zope.interface.verify import verifyObject

class Test(IInterfaceServiceTests, unittest.TestCase):
    """Test Interface for InterfaceService Instance."""

    def getServices(self):
        s = InterfaceService()
        return s, s

    def testInterfaceVerification(self):
        verifyObject(IGlobalInterfaceService, InterfaceService())

def test_suite():
    return unittest.makeSuite(Test)
