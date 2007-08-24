##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Functional tests for the site management.

$Id$
"""
__docformat__ = "reStructuredText"

import os.path
import unittest

from zope.testing import doctest
from zope.app.testing import functional


AppComponentBrowserLayer = functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'AppComponentBrowserLayer', allow_teardown=True)


def test_suite():
    site = functional.FunctionalDocFileSuite(
        "site.txt",
        optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
    site.layer = AppComponentBrowserLayer
    return site


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
