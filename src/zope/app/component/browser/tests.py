##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Registration functional tests

$Id$
"""

import unittest
import zope.app.testing.functional
from zope.app.component.testing import AppComponentLayer

from zope import interface

class ISampleBase(interface.Interface):
    pass

class ISample(ISampleBase):
    pass

class Sample:
    interface.implements(ISample)


def test_suite():
    suite = zope.app.testing.functional.FunctionalDocFileSuite(
        'registration.txt')
    suite.layer = AppComponentLayer
    return suite
        
if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

