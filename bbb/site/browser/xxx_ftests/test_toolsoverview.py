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
"""Tools Overview Functional Tests

$Id$
"""
import unittest

from zope.app.tests.functional import BrowserTestCase


class TestToolsOverview(BrowserTestCase):

    def testToolsOverview(self):
        path = '/++etc++site/@@tools.html'
        # create the view
        response = self.publish(path, basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)

        body = response.getBody()

        # test for broken links
        self.checkForBrokenLinks(body, path, basic='mgr:mgrpw')

        # We can't really test more here, since we do not know what type of
        # utilities will registered as tools.


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestToolsOverview))
    return suite

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
