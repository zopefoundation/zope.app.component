##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Unit tests for service summary view

$Id$
"""
import unittest
from zope.app.tests import ztapi
from zope.publisher.browser import TestRequest
from zope.app.tests import setup
from zope.app.site.interfaces import ILocalService
from zope.interface import implements

class ServiceStub(object):
    __parent__ = None
    __name__ = None
    next = None
    implements(ILocalService)

class TestServices(unittest.TestCase):

    def setUp(self):
        root = setup.placefulSetUp(True)
        self.sm = setup.createServiceManager(root)
        setup.addService(self.sm, 'Utilities', ServiceStub())

    def tearDown(self):
        setup.placefulTearDown()

    def test(self):
        from zope.app.site.browser import gatherConfiguredServices
        expected = [{'url': '', 'disabled': False, 'manageable': False,
                     'name': 'Adapters', 'parent': u'global'},
                    {'url': '', 'disabled': False, 'manageable': False,
                     'name': 'Services', 'parent': u'global'},
                    {'url': 'http://127.0.0.1/++etc++site/default/Utilities',
                     'disabled': False, 'manageable': True,
                     'name': 'Utilities', 'parent': u'parent'}]
        request = TestRequest()
        results = gatherConfiguredServices(self.sm, request)
        self.assertEqual(results, expected)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestServices))
    return suite


if __name__ == '__main__':
    unittest.main()
