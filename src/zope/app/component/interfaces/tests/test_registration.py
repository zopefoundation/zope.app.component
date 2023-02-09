#############################################################################
#
# Copyright (c) 2017 Zope Foundation and Contributors.
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

import unittest

from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


class TestComponent(unittest.TestCase):

    def test_implements(self):
        from zope.app.component.interfaces.registration import Component
        from zope.app.component.interfaces.registration import IComponent

        verifyClass(IComponent, Component)
        verifyObject(IComponent, Component())


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
