##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Registered components tests

$Id$
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.registration.registration import Registered
from zope.app.annotation.interfaces import IAnnotations
from zope.app.traversing.interfaces import ITraverser
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.interface import implements
from zope.app.container.contained import Contained

class C(dict, Contained):

    __name__ = __parent__ = None
    
    implements(IAnnotations, ITraverser)

    def __init__(self, testobjs={}):
        self.testobjs = testobjs

    def traverse(self, path, default=None, request=None):
        return self.testobjs[path]
        

class TestRegistered(PlacelessSetup, TestCase):

    def testVerifyInterface(self):
        from zope.interface.verify import verifyObject
        from zope.app.registration.interfaces import IRegistered
        obj = Registered(C())
        verifyObject(IRegistered, obj)

    def testBasic(self):
        a_b = 12
        c_d = 24
        c_e = 36
        obj = Registered(C({'/a/b': a_b,
                            '/c/d': c_d,
                            '/c/e': c_e,
                            }))
        self.failIf(obj.usages())
        obj.addUsage('/a/b')
        obj.addUsage('/c/d')
        obj.addUsage('/c/e')
        obj.addUsage('/c/d')
        locs = list(obj.usages())
        locs.sort()
        self.assertEqual(locs, ['/a/b', '/c/d', '/c/e'])
        regs = list(obj.registrations())
        self.assertEqual(len(regs), 3)
        self.assert_(a_b in regs)
        self.assert_(c_d in regs)
        self.assert_(c_e in regs)

        obj.removeUsage('/c/d')
        locs = list(obj.usages())
        locs.sort()
        self.assertEqual(locs, ['/a/b', '/c/e'])
        regs = list(obj.registrations())
        self.assertEqual(len(regs), 2)
        self.assert_(a_b in regs)
        self.assert_(c_d not in regs)
        self.assert_(c_e in regs)

        obj.removeUsage('/c/d')
        locs = list(obj.usages())
        locs.sort()
        self.assertEqual(locs, ['/a/b', '/c/e'])
        self.assertEqual(len(regs), 2)
        self.assert_(a_b in regs)
        self.assert_(c_d not in regs)
        self.assert_(c_e in regs)

    def testRelativeAbsolute(self):
        obj = Registered(C())
        # Hack the object to have a parent path
        obj.pp = "/a/"
        obj.pplen = len(obj.pp)
        obj.addUsage("foo")
        self.assertEqual(obj.usages(), ("/a/foo",))
        obj.removeUsage("/a/foo")
        self.assertEqual(obj.usages(), ())
        obj.addUsage("/a/bar")
        self.assertEqual(obj.usages(), ("/a/bar",))
        obj.removeUsage("bar")
        self.assertEqual(obj.usages(), ())

def test_suite():
    return makeSuite(TestRegistered)

if __name__=='__main__':
    main(defaultTest='test_suite')
