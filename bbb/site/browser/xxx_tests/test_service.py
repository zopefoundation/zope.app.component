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
"""Unit tests for service adding and registration views.

$Id$
"""
import unittest
from zope.app.tests import ztapi
from zope.interface import Interface, implements
from zope.publisher.browser import TestRequest
from zope.app.tests.placelesssetup import PlacelessSetup, setUp, tearDown
from zope.testing.doctestunit import DocTestSuite

class IFoo(Interface):
    pass

class Foo(object):
    implements(IFoo)
    def __init__(self, url='some_url'):
        self.url = url

class TestComponentAdding(PlacelessSetup, unittest.TestCase):

    def test_nextURL(self):
        from zope.app.site.browser import ComponentAdding

        class AU(object):
            def __init__(self, context, request):
                self.context = context
            def __str__(self):
                return self.context.url
            __call__ = __str__
        ztapi.browserView(IFoo, 'absolute_url', AU)
        ztapi.browserView(IFoo, 'registration.html', AU)

        context = Foo('foo_url')
        request = TestRequest()
        view = ComponentAdding(context, request)
        view.added_object = None
        self.assertEquals(view.nextURL(), 'foo_url/@@contents.html')

        view.added_object = Foo('bar_url')
        self.assertEquals(view.nextURL(), 'bar_url/@@registration.html')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestComponentAdding))
    suite.addTest(DocTestSuite('zope.app.site.browser',
                               setUp=setUp, tearDown=tearDown))
    return suite


if __name__ == '__main__':
    unittest.main()
