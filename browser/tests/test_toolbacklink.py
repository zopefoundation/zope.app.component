# -*- coding: latin-1 -*-
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
"""Tool backlink generation tests

$Id$
"""

import unittest

from zope.interface import implements, Interface
from zope.app.utility.interfaces import ILocalUtility
from zope.publisher.browser import TestRequest
from zope.app.component.interface import provideInterface
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.site.browser.tools import IToolType, ToolsBacklink
from zope.component.interfaces import IServiceService
from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.tests import ztapi

class IDummyUtility(Interface):
    pass

class DummyUtility(object):
    implements(IDummyUtility, ILocalUtility)

class Locatable(object):
    def __init__(self, context):
        pass
    
    def getPath(self):
        return '/++etc++site'
    
class TestBackLink(PlacelessSetup, unittest.TestCase):
    def setUp(self):
        super(TestBackLink, self).setUp()
        provideInterface(None, IDummyUtility, IToolType)
        ztapi.provideAdapter(IServiceService, IPhysicallyLocatable, Locatable)
        
    def testLink(self):
        view = ToolsBacklink()
        view.request = TestRequest()
        view.context = DummyUtility()

        location = view.getLink()

        # inspect the response
        self.assertEqual(location, '/++etc++site/manageIDummyUtilityTool.html')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBackLink))
    return suite


if __name__ == '__main__':
    unittest.main()

