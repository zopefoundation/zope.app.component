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
"""Utility service tests

$Id$
"""
import unittest
from StringIO import StringIO
from persistent.interfaces import IPersistent

from zope.component import getService
from zope.component.exceptions import ComponentLookupError
from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.interface import Interface, implements
from zope.testing.doctestunit import DocTestSuite

import zope.app.security
import zope.app.utility
from zope.app.tests import setup
from zope.app import utility, zapi
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.dependable.interfaces import IDependable
from zope.app.location.interfaces import ILocation
from zope.app.traversing.api import traverse
from zope.app.registration.interfaces import IRegistrationStack
from zope.app.registration.interfaces import UnregisteredStatus
from zope.app.registration.interfaces import RegisteredStatus
from zope.app.registration.interfaces import ActiveStatus
from zope.app.registration.interfaces import IRegistered
from zope.app.site.tests import placefulsetup
from zope.app.tests import setup
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.utility.interfaces import ILocalUtility


def configfile(s):
    return StringIO("""<configure
      xmlns='http://namespaces.zope.org/zope'
      i18n_domain='zope'>
      %s
      </configure>
      """ % s)

class IFo(Interface): pass

class IFoo(IFo):
    def foo(self): pass

class IBar(Interface): pass


class Foo(object):
    # We implement IRegistered and IDependable directly to
    # depend as little  as possible on other infrastructure.
    __name__ = __parent__ = None
    implements(IFoo, ILocalUtility, IRegistered, IDependable)
    
    def __init__(self, name):
        self.name = name
        self._usages = []
        self._dependents = []

    def foo(self):
        return 'foo ' + self.name

    def addUsage(self, location):
        "See zope.app.registration.interfaces.IRegistered"
        if location not in self._usages:
            self._usages.append(location)

    def removeUsage(self, location):
        "See zope.app.registration.interfaces.IRegistered"
        self._usages.remove(location)

    def usages(self):
        "See zope.app.registration.interfaces.IRegistered"
        return self._usages

    def addDependent(self, location):
        "See zope.app.dependable.interfaces.IDependable"
        if location not in self._dependents:
            self._dependents.append(location)

    def removeDependent(self, location):
        "See zope.app.dependable.interfaces.IDependable"
        self._dependents.remove(location)

    def dependents(self):
        "See zope.app.dependable.interfaces.IDependable"
        return self._dependents


class UtilityStub(object):
    implements(ILocation, IPersistent)


class TestUtilityService(placefulsetup.PlacefulSetup, unittest.TestCase):

    def setUp(self):
        sm = placefulsetup.PlacefulSetup.setUp(self, site=True)
        setup.addService(sm, zapi.servicenames.Utilities,
                         utility.LocalUtilityService())

    def test_queryUtility_delegates_to_global(self):
        utilityService = zapi.getGlobalService(zapi.servicenames.Utilities)
        utilityService.provideUtility(IFoo, Foo("global"))
        utilityService.provideUtility(IFoo, Foo("global bob"),
                                            name="bob")

        utility_service = getService("Utilities", self.rootFolder)

        # We changed the root (base) service. This doesn't normally
        # occur.  We have to notify the local service that the base
        # has changes:
        utility_service.baseChanged()
        
        self.assert_(utility_service != utilityService)

        self.assertEqual(utility_service.queryUtility(IFoo).foo(),
                         "foo global")
        self.assertEqual(utility_service.queryUtility(IFoo, "bob").foo(),
                         "foo global bob")
        self.assertEqual(utility_service.queryUtility(IFo).foo(),
                         "foo global")
        self.assertEqual(utility_service.queryUtility(IFo, "bob").foo(),
                         "foo global bob")

        self.assertEqual(utility_service.queryUtility(IBar), None)
        self.assertEqual(utility_service.queryUtility(IBar, "bob"), None)
        self.assertEqual(utility_service.queryUtility(IFoo, "rob"), None)

    def test_getUtility_delegates_to_global(self):
        utilityService = zapi.getGlobalService(zapi.servicenames.Utilities)
        utilityService.provideUtility(IFoo, Foo("global"))
        utilityService.provideUtility(IFoo, Foo("global bob"),
                                            name="bob")

        utility_service = getService("Utilities", self.rootFolder)
        self.assert_(utility_service != utilityService)

        self.assertEqual(utility_service.getUtility(IFoo).foo(),
                         "foo global")
        self.assertEqual(utility_service.getUtility(IFoo, "bob").foo(),
                         "foo global bob")
        self.assertEqual(utility_service.getUtility(IFo).foo(),
                         "foo global")
        self.assertEqual(utility_service.getUtility(IFo, "bob").foo(),
                         "foo global bob")


        self.assertRaises(ComponentLookupError,
                          utility_service.getUtility, IBar)
        self.assertRaises(ComponentLookupError,
                          utility_service.getUtility, IBar, 'bob')
        self.assertRaises(ComponentLookupError,
                          utility_service.getUtility, IFoo, 'rob')


    def test_registrationsFor_methods(self):
        utilities = getService("Utilities", self.rootFolder)
        default = traverse(self.rootFolder, "++etc++site/default")
        default['foo'] = Foo("local")
        foo = default['foo']

        for name in ('', 'bob'):
            registration = utility.UtilityRegistration(name, IFoo, foo)
            self.assertEqual(utilities.queryRegistrationsFor(registration),
                             None)
            registery = utilities.createRegistrationsFor(registration)
            self.assert_(IRegistrationStack.providedBy(registery))
            self.assertEqual(utilities.queryRegistrationsFor(registration),
                             registery)


    def test_local_utilities(self):
        utilityService = zapi.getGlobalService(zapi.servicenames.Utilities)
        utilityService.provideUtility(IFoo, Foo("global"))
        utilityService.provideUtility(IFoo, Foo("global bob"),
                                            name="bob")

        utilities = getService("Utilities", self.rootFolder)

        # We changed the root (base) service. This doesn't normally
        # occur.  We have to notify the local service that the base
        # has changes:
        utilities.baseChanged()

        default = traverse(self.rootFolder, "++etc++site/default")
        default['foo'] = Foo("local")
        foo = default['foo']
        cm = default.getRegistrationManager()

        for name in ('', 'bob'):
            registration = utility.UtilityRegistration(name, IFoo, foo)
            cname = cm.addRegistration(registration)
            registration = traverse(cm, cname)

            gout = name and "foo global "+name or "foo global"

            self.assertEqual(utilities.getUtility(IFoo, name).foo(), gout)

            registration.status = ActiveStatus

            self.assertEqual(utilities.getUtility(IFoo, name).foo(),
                             "foo local")

            registration.status = RegisteredStatus

            self.assertEqual(utilities.getUtility(IFoo, name).foo(), gout)


    def test_local_overrides(self):
        # Make sure that a local utility service can override another
        sm1 = zapi.traverse(self.rootFolder, "++etc++site")
        setup.addUtility(sm1, 'u1', IFoo, Foo('u1'))
        setup.addUtility(sm1, 'u2', IFoo, Foo('u2'))
        sm2 = self.makeSite('folder1')
        setup.addService(sm2, zapi.servicenames.Utilities,
                         utility.LocalUtilityService())
        setup.addUtility(sm2, 'u2', IFoo, Foo('u22'))

        # Make sure we acquire:
        self.assertEqual(zapi.getUtility(IFoo, 'u1', sm2).name, 'u1')

        # Make sure we override:
        self.assertEqual(zapi.getUtility(IFoo, 'u2', sm2).name, 'u22')


class TestLocalUtilityDirective(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(TestLocalUtilityDirective, self).setUp()
        XMLConfig('meta.zcml', zope.app.component)()
        XMLConfig('meta.zcml', zope.app.utility)()

    def testDirective(self):
        f = configfile('''
        <localUtility
            class="zope.app.utility.tests.UtilityStub">
        </localUtility>
        ''')
        xmlconfig(f)
        self.assert_(ILocalUtility.implementedBy(UtilityStub))
        self.assert_(IAttributeAnnotatable.implementedBy(UtilityStub))
    

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestUtilityService),
        unittest.makeSuite(TestLocalUtilityDirective),
        DocTestSuite('zope.app.utility.metaconfigure'),
        DocTestSuite('zope.app.utility.utility',
                     setUp=setup.placelessSetUp,
                     tearDown=setup.placelessTearDown),
        DocTestSuite('zope.app.utility.vocabulary',
                     setUp=setup.placelessSetUp,
                     tearDown=setup.placelessTearDown)
        ))

if __name__ == '__main__':
    unittest.main(default='test_suite')
