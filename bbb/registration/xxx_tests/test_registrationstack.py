##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Registration Stack tests

$Id$
"""
from unittest import TestCase, TestSuite, main, makeSuite

from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.tests import ztapi
from zope.app.traversing.api import traverse

from zope.app.registration.registration import RegistrationStack
from zope.app.registration import interfaces

class Registration(object):

    active = 0
    registry = None


def handleActivated(event):
    reg = event.object
    if (reg.registry is not None) and (reg.registry.active() != reg):
        raise AssertionError("Told active but not the active registration")
    reg.active += 1

def handleDeactivated(event):
    reg = event.object
    if (reg.registry is not None) and (reg.registry.active() == reg):
        raise AssertionError(
            "Told deactivated but still the active registration")
    reg.active -= 1


class Test(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self, site=True)
        ztapi.subscribe((interfaces.IRegistrationActivatedEvent,), None,
                        handleActivated)
        ztapi.subscribe((interfaces.IRegistrationDeactivatedEvent,), None,
                        handleDeactivated)

        root = self.rootFolder
        self.__default = traverse(root, "++etc++site/default")
        self.__registry = RegistrationStack(root)

    def __config(self, name):
        self.__default[name] = Registration()
        return self.__default[name]

    def test_register_and_registered_and_nonzero_and_active(self):
        registry = self.__registry

        self.assertEqual(registry.active(), None)

        self.failIf(registry)
        self.__c1 = c1 = self.__config("1")
        c1.registry = registry
        registry.register(c1)
        self.failUnless(registry)
        self.failUnless(registry.registered(c1))
        self.assertEqual(c1.active, 0)

        self.assertEqual(registry.active(), None)

        self.__c2 = c2 = self.__config("2")
        c2.registry = registry
        self.failIf(registry.registered(c2))
        registry.register(c2)
        self.failUnless(registry)
        self.failUnless(registry.registered(c2))
        self.assertEqual(c2.active, 0)


    def test_unregister_and_registered_and_nonzero(self):
        # reuse registration test to set things up (more)
        self.test_register_and_registered_and_nonzero_and_active()

        registry = self.__registry

        c1 = self.__c1
        registry.unregister(c1)
        self.failIf(registry.registered(c1))
        self.assertEqual(c1.active, 0)

        c2 = self.__c2
        registry.unregister(c2)
        self.failIf(registry.registered(c2))
        self.assertEqual(c2.active, 0)

        self.failIf(registry)

    def test_activate_and_active(self):
        # reuse registration test to set things up (more)
        self.test_register_and_registered_and_nonzero_and_active()

        registry = self.__registry
        self.assertEqual(registry.active(), None)

        c1 = self.__c1
        c2 = self.__c2

        registry.activate(c2)
        self.assertEqual(c1.active, 0)
        self.failUnless(registry.registered(c1))
        self.assertEqual(c2.active, 1)
        self.failUnless(registry.registered(c2))
        self.assertEqual(registry.active(), c2)

        registry.activate(c2)
        self.assertEqual(c1.active, 0)
        self.failUnless(registry.registered(c1))
        self.assertEqual(c2.active, 1)
        self.failUnless(registry.registered(c2))
        self.assertEqual(registry.active(), c2)

        registry.activate(c1)
        self.assertEqual(c1.active, 1)
        self.failUnless(registry.registered(c1))
        self.assertEqual(c2.active, 0)
        self.failUnless(registry.registered(c2))
        self.assertEqual(registry.active(), c1)

    def test_activate_none(self):
        self.test_activate_and_active()

        registry = self.__registry
        c1 = self.__c1
        c2 = self.__c2

        registry.activate(None)

        self.assertEqual(c1.active, 0)
        self.failUnless(registry.registered(c1))
        self.assertEqual(c2.active, 0)
        self.failUnless(registry.registered(c2))
        self.assertEqual(registry.active(), None)

    def test_activate_unregistered(self):
        registry = self.__registry
        self.assertRaises(ValueError, registry.activate, self.__config('3'))
        self.test_activate_and_active()
        self.assertRaises(ValueError, registry.activate, self.__config('4'))

    def test_deactivate(self):
        self.test_activate_and_active()

        registry = self.__registry
        c1 = self.__c1
        c2 = self.__c2
        self.assertEqual(registry.active(), c1)

        registry.deactivate(c2)
        self.assertEqual(c2.active, 0)
        self.assertEqual(registry.active(), c1)

        registry.deactivate(c1)
        self.assertEqual(c1.active, 0)
        self.assertEqual(c2.active, 1)
        self.assertEqual(registry.active(), c2)

        self.failUnless(registry.registered(c1))
        self.failUnless(registry.registered(c2))

    def test_unregister_active(self):
        self.test_activate_and_active()

        registry = self.__registry
        c1 = self.__c1
        c2 = self.__c2
        self.assertEqual(registry.active(), c1)

        registry.unregister(c1)
        self.assertEqual(c1.active, 0)
        self.assertEqual(c2.active, 1)
        self.assertEqual(registry.active(), c2)

        self.failIf(registry.registered(c1))
        self.failUnless(registry.registered(c2))

    def test_deactivate_unregistered(self):
        registry = self.__registry
        self.assertRaises(ValueError, registry.deactivate, self.__config('3'))

    def test_info(self):
        self.test_activate_and_active()

        registry = self.__registry
        c1 = self.__c1
        c2 = self.__c2

        info = registry.info()
        self.assertEqual(
            info,
            [
              {'active': True,
               'registration': c1,
               },
              {'active': False,
               'registration': c2,
               },
              ])

        registry.deactivate(c1)

        info = registry.info()
        self.assertEqual(
            info,
            [
              {'active': True,
               'registration': c2,
               },
              {'active': False,
               'registration': c1,
               },
              ])

    def test_avoid_duplicate_activation(self):
        # Test for a specific bug that used to exist:
        # when unregistering an inactive registration, don't
        # re-activate the registration that's already active
        c1 = self.__config('1')
        c2 = self.__config('2')
        registry = self.__registry
        registry.register(c1)
        registry.register(c2)
        registry.activate(c1)
        self.assertEqual(c1.active, 1)
        self.assertEqual(c2.active, 0)
        registry.unregister(c2)
        self.assertEqual(c1.active, 1)
        self.assertEqual(c2.active, 0)


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
