##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Functional tests

$Id$
"""
import unittest
from zope.app.testing import functional


class RegistrationViewTests(functional.BrowserTestCase):

    def testRegistrationView(self):
        response = self.publish(
            '/++etc++site/default/++registrations++/@@index.html',
            basic='mgr:mgrpw',
            handle_errors=True)
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('Registration Manager' in body)


def test_suite():
    return unittest.makeSuite(RegistrationViewTests)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
