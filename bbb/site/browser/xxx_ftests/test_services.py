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
"""Services overview functional tests

$Id$
"""
import unittest

from zope.app.tests.functional import BrowserTestCase


class TestServices(BrowserTestCase):

    def test(self):
        path = '/++etc++site/@@services.html'
        # create the view
        response = self.publish(path, basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)

        body = response.getBody()

        # test for broken links
        self.checkForBrokenLinks(body, path, basic='mgr:mgrpw')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestServices))
    return suite

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
