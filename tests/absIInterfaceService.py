##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Abstract test class for IInterfaceService."""

from zope.component.exceptions import ComponentLookupError
from zope.app.interfaces.component import IInterfaceService
from zope.interface import Interface
from zope.interface.verify import verifyObject

class B(Interface):
    pass

class I(Interface):
    """bah blah
    """

class I2(B):
    """eek
    """

class I3(B):
    """
    """
    def one():
        """method one"""

    def two():
        """method two"""

class IInterfaceServiceTests:

    def getServices(self):
        # Return pair of services, one to query, one to update.
        raise NotImplementedError
    
    def testVerifyIInterfaceService(self):
        verifyObject(IInterfaceService, self.getServices()[0])

    def listEq(self, iterable, expectedlist):
        self.assertEqual(list(iterable), expectedlist)

    def testInterfaceService(self):
        rservice, wservice = self.getServices()

        self.assertRaises(ComponentLookupError,
                          rservice.getInterface, 'Foo.Bar')
        self.assertEqual(rservice.queryInterface('Foo.Bar'), None)
        self.assertEqual(rservice.queryInterface('Foo.Bar', 42), 42)
        self.failIf(rservice.searchInterface(''))

        wservice.provideInterface('Foo.Bar', I)

        self.assertEqual(rservice.getInterface('Foo.Bar'), I)
        self.assertEqual(rservice.queryInterface('Foo.Bar'), I)
        self.listEq(rservice.searchInterface(''), [I])
        self.listEq(rservice.searchInterface(base=B), [])

        wservice.provideInterface('Foo.Baz', I2)

        result = list(rservice.searchInterface(''))
        result.sort()
        self.assertEqual(result, [I, I2])

        self.listEq(rservice.searchInterface('I2'), [I2])
        self.listEq(rservice.searchInterface('eek'), [I2])

        self.listEq(rservice.searchInterfaceIds('I2'), ['Foo.Baz'])
        self.listEq(rservice.searchInterfaceIds('eek'), ['Foo.Baz'])

        self.listEq(rservice.items("I2"), [("Foo.Baz", I2)])
        self.listEq(rservice.items("eek"), [("Foo.Baz", I2)])

        wservice.provideInterface('Foo.Bus', I3)
        self.listEq(rservice.searchInterface('two'), [I3])
        self.listEq(rservice.searchInterface('two', base=B), [I3])
        self.listEq(rservice.items("two", base=B), [("Foo.Bus", I3)])

        r = list(rservice.searchInterface(base=B))
        r.sort()
        self.assertEqual(r, [I2, I3])
