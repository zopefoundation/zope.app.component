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
"""Sample adapter class for testing

$Id$
"""

import zope.interface

class I1(zope.interface.Interface):
    pass

class I2(zope.interface.Interface):
    pass

class I3(zope.interface.Interface):
    pass

class IS(zope.interface.Interface):
    pass


class Adapter(object):
    def __init__(self, *args):
        self.context = args

class A1(Adapter):
    zope.interface.implements(I1)

class A2(Adapter):
    zope.interface.implements(I2)

class A3(Adapter):
    zope.interface.implements(I3)


def Handler(content, *args):
    # uninteresting handler
    content.args = getattr(content, 'args', ()) + (args, )
