##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""

$Id: service.py,v 1.2 2002/12/25 14:12:46 jim Exp $
"""
__metaclass__ = type # All classes are new style when run with Python 2.2+

from zope.interface import Interface

class IFooService(Interface):

    def foo(): pass
    def foobar(): pass

class FooService:

    __implements__ = IFooService

    def foo(self): return "foo here"
    def foobar(self): return "foobarred"

    def bar(self): return "you shouldn't get this"

fooService = FooService()

class Foo2(FooService): pass

foo2 = Foo2()
