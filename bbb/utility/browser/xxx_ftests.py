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
"""Tests for zope.app.utility.browser."""

import unittest

import transaction

import zope.app.securitypolicy.interfaces
import zope.app.securitypolicy.role

from zope.app import zapi

from zope.app.tests import functional


class UtilityViewTestCase(functional.BrowserTestCase):

    def test_utilities_view(self):
        # need to add and activate a role utility
        root = self.getRootFolder()
        default = zapi.traverse(root, "/++etc++site/default")
        role = zope.app.securitypolicy.role.PersistentRole("my-sample-role")
        default["my-role"] = role
        reg = zope.app.securitypolicy.role.RoleRegistration(
            "my-role-registration",
            zope.app.securitypolicy.interfaces.IRole,
            default["my-role"])
        rm = default.getRegistrationManager()
        rm.addRegistration(reg)
        reg.status = "Active"
        transaction.get_transaction().commit()
        # now let's take a look at the Utilities page:
        response = self.publish(
            "/++etc++site/default/Utilities/@@utilities.html",
            basic="mgr:mgrpw")
        self.assertEqual(response.getStatus(), 200)


def test_suite():
    suite = unittest.makeSuite(UtilityViewTestCase)
    suite.addTest(functional.FunctionalDocFileSuite("utilities.txt"))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
