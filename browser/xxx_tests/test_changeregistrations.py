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
"""Registration Change Tests

$Id$
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.publisher.browser import TestRequest
from zope.app.registration.tests.registrationstack \
     import TestingRegistrationStack, TestingRegistration
from zope.app.registration.browser import ChangeRegistrations

a = TestingRegistration('a')
b = TestingRegistration('b')
c = TestingRegistration('c')

class Test(TestCase):

    def test_applyUpdates_and_setPrefix(self):
        registry = TestingRegistrationStack(a, b, c)
        request = TestRequest()
        view = ChangeRegistrations(registry, request)
        view.setPrefix("Pigs")

        # Make sure we don't apply updates unless asked to
        request.form = {'Pigs.active': 'disable'}
        view.applyUpdates()
        data = [(info['active'], info['registration'])
                for info in registry.info()]
        self.assertEqual(data, [(True, a), (False, b), (False, c)])

        # Now test disabling
        request.form = {'submit_update': '', 'Pigs.active': 'disable'}
        view.applyUpdates()
        data = [(info['active'], info['registration'])
                for info in registry.info()]
        self.assertEqual(data, [(False, a), (False, b), (False, c)])

        # Now test enabling c
        request.form = {'submit_update': '', 'Pigs.active': 'c'}
        view.applyUpdates()
        data = [(info['active'], info['registration'])
                for info in registry.info()]
        self.assertEqual(data, [(True, c), (False, a), (False, b)])


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
