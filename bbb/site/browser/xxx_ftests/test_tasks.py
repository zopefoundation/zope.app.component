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
"""Site Tasks functional tests

$Id: test_services.py 25177 2004-06-02 13:17:31Z jim $
"""
import unittest

from zope.app.tests.functional import BrowserTestCase


class TasksTest(BrowserTestCase):

    def testTasks(self):
        path = '/++etc++site/@@tasks.html'
        response = self.publish(path, basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)

        body = response.getBody()
        self.assert_('Common Site Management' in body)
        self.checkForBrokenLinks(body, path, basic='mgr:mgrpw')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TasksTest))
    return suite

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
