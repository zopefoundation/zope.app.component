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
"""Registration Tests

$Id$
"""
__docformat__ = "reStructuredText"

import unittest
import warnings

import zope.component.testing as placelesssetup
from zope.testing import doctest
from zope.app.testing import setup

def setUp(test):
    placelesssetup.setUp(test)
    setup.setUpAnnotations()
    setup.setUpDependable()
    setup.setUpTraversal()
    test.globs['showwarning'] = warnings.showwarning
    warnings.showwarning = lambda *a, **k: None

def tearDown(test):
    warnings.showwarning = test.globs['showwarning']
    placelesssetup.tearDown(test)

def test_suite():
    suite = unittest.TestSuite((
        doctest.DocFileSuite('deprecated35_statusproperty.txt',
                             'deprecated35_registration.txt',
                             setUp=setUp, tearDown=tearDown),
        ))
    suite.level = 2
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
