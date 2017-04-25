##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Registration functional tests
"""


import doctest
import unittest

from zope.testbrowser.wsgi import TestBrowserLayer
from zope.app.wsgi.testlayer import BrowserLayer

import zope.app.component.browser
import zope.app.component.testing


class _AppComponentBrowserLayer(TestBrowserLayer,
                                BrowserLayer):

    def setUp(self):
        # Typically this would be done by zope.app.principalannotation's
        # bootstrap.zcml but we don't have a dep on that.
        super(_AppComponentBrowserLayer, self).setUp()
        from zope.principalannotation.utility import PrincipalAnnotationUtility
        from zope.principalannotation.interfaces import IPrincipalAnnotationUtility
        from zope import component
        component.getGlobalSiteManager().registerUtility(PrincipalAnnotationUtility(),
                                                         IPrincipalAnnotationUtility)


AppComponentBrowserLayer = _AppComponentBrowserLayer(
    zope.app.component.browser,
    allowTearDown=True)

from zope.testing import renormalizing

import re
checker = renormalizing.RENormalizing([
    (re.compile("u('.*?')"), r"\1"),
    (re.compile('u(".*?")'), r"\1"),
])

def test_suite():
    flags = optionflags=(doctest.ELLIPSIS
                         | doctest.NORMALIZE_WHITESPACE
                         | renormalizing.IGNORE_EXCEPTION_MODULE_IN_PYTHON2)

    site = doctest.DocFileSuite(
        "../site.rst",
        globs={'getRootFolder': AppComponentBrowserLayer.getRootFolder},
        optionflags=flags,
        checker=checker)
    site.layer = AppComponentBrowserLayer
    make_site = doctest.DocTestSuite(zope.app.component.browser,
                                     optionflags=flags,
                                     checker=checker)

    return unittest.TestSuite((site, make_site,))
