##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Registration Manager tests

$Id$
"""
from unittest import TestSuite, TestCase, main, makeSuite
from doctest import DocTestSuite
from zope.app.registration.interfaces import IRegistrationManager
from zope.app.registration.registration import RegistrationManager
from zope.app.site.tests import placefulsetup
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.traversing.api import traverse
from zope.interface.common.tests.basemapping import BaseTestIEnumerableMapping
from zope.interface.verify import verifyObject
from zope.interface import implements
from zope.app.container.contained import ObjectRemovedEvent

class Test(BaseTestIEnumerableMapping, PlacelessSetup, TestCase):
    """Testing for Registration Manager """

    def setUp(self):
        super(Test, self).setUp()
        self.__manager = manager = RegistrationManager()
        self.names = []
        self.stateDict = {}
        for ltr in 'abcdefghijklmnop':
            name = manager.addRegistration(ltr)
            self.names.append(name)
            self.stateDict[name] = ltr
        n = self.names.pop(9); del manager[n]; del self.stateDict[n] # 'str10'
        n = self.names.pop(7); del manager[n]; del self.stateDict[n] # 'str8'

    def test_implements_IRegistrationManager(self):
        verifyObject(IRegistrationManager, self.__manager)

    def _IEnumerableMapping__stateDict(self):
        # Hook needed by BaseTestIEnumerableMapping
        # also, effectively test __setitem__ and __delitem__.
        return self.stateDict

    def _IEnumerableMapping__sample(self):
        # Hook needed by BaseTestIEnumerableMapping
        # also, effectively test __setitem__ and __delitem__.
        return self.__manager

    def _IEnumerableMapping__absentKeys(self):
        # Hook needed by BaseTestIEnumerableMapping
        # also, effectively test __setitem__ and __delitem__.
        return ['-1', '8', '10', '17', '100', '10000']

    #########################################################
    # Move Top

    def test_moveTop_nothing(self):
        self.__manager.moveTop([])
        self.assertEqual(
            list(self.__manager.keys()),
            self.names,
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveTop_1_no_effect(self):
        self.__manager.moveTop([self.names[0]])
        self.assertEqual(
            list(self.__manager.keys()),
            self.names,
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveTop_many_no_effect(self):
        names = self.names
        self.__manager.moveTop([names[0], 'str88',
                                names[2], names[1], 'str99'])
        self.assertEqual(
            list(self.__manager.keys()),
            names,
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveTop_1(self):
        names = self.names[:]
        name = names.pop(2)
        names.insert(0, name)
        self.__manager.moveTop([name])
        self.assertEqual(
            list(self.__manager.keys()),
            names,
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveTop_many(self):
        names = self.names[:]
        n14 = names.pop(13)
        n13 = names.pop(12)
        n9 = names.pop(9)
        n3 = names.pop(3)
        n2 = names.pop(2)
        n0 = names.pop(0)
        move_names = [n0, n2, 'str88', n3, n9, n13, n14, 'str99']
        self.__manager.moveTop(move_names)
        self.assertEqual(
            list(self.__manager.keys()),
            [n0, n2, n3, n9, n13, n14] + names,
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveTop_one_element_container(self):
        manager = RegistrationManager()
        name = manager.addRegistration('a')
        manager.moveTop([name])
        self.assertEqual(list(manager.items()), [(name, 'a')])

    #########################################################
    # Move Bottom

    def test_moveBottom_nothing(self):
        self.__manager.moveBottom([])
        self.assertEqual(
            list(self.__manager.keys()),
            self.names,
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveBottom_1_no_effect(self):
        self.__manager.moveBottom([self.names[-1]])
        self.assertEqual(
            list(self.__manager.keys()),
            self.names,
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveBottom_many_no_effect(self):
        names = self.names
        self.__manager.moveBottom([names[11], 'str88',
                                   names[13], names[12], 'str99'])
        self.assertEqual(
            list(self.__manager.keys()),
            self.names,
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveBottom_1(self):
        names = self.names[:]
        name = names.pop(2)
        names.append(name)
        self.__manager.moveBottom([name])
        self.assertEqual(
            list(self.__manager.keys()),
            names,
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveBottom_many(self):
        names = self.names[:]
        n13 = names.pop(13)
        n12 = names.pop(12)
        n9 = names.pop(9)
        n3 = names.pop(3)
        n2 = names.pop(2)
        n0 = names.pop(0)
        self.__manager.moveBottom(
            [n0, n2, 'str88', n3, n9, n13, n12, 'str99'])
        self.assertEqual(
            list(self.__manager.keys()),
            names + [n0, n2, n3, n9, n12, n13],
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveBottom_one_element_container(self):
        manager = RegistrationManager()
        name = manager.addRegistration('a')
        manager.moveBottom([name])
        self.assertEqual(list(manager.items()), [(name, 'a')])

    #########################################################
    # Move Up

    def test_moveUp_nothing(self):
        self.__manager.moveUp([])
        self.assertEqual(
            list(self.__manager.keys()),
            self.names,
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveUp_1_no_effect(self):
        self.__manager.moveUp([self.names[0]])
        self.assertEqual(
            list(self.__manager.keys()),
            self.names,
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveUp_many_no_effect(self):
        names = self.names
        self.__manager.moveUp([names[0], 'str88', names[2], names[1], 'str99'])
        self.assertEqual(
            list(self.__manager.keys()),
            self.names,
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveUp_1(self):
        names = self.names[:]
        n2 = names.pop(2)
        names.insert(1, n2)
        self.__manager.moveUp([n2])
        self.assertEqual(
            list(self.__manager.keys()),
            names,
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveUp_many(self):
        names = self.names
        self.__manager.moveUp(
            [names[0], names[2], 'str88', names[3], names[8],
             names[13], names[12], 'str99'])
        self.assertEqual(
            list(self.__manager.keys()),
            [names[0], names[2], names[3], names[1], names[4],
             names[5], names[6], names[8], names[7], names[9],
             names[10], names[12], names[13], names[11]],
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveUp_one_element_container(self):
        manager = RegistrationManager()
        name = manager.addRegistration('a')
        manager.moveUp([name])
        self.assertEqual(list(manager.items()), [(name, 'a')])

    #########################################################
    # Move Down

    def test_moveDown_nothing(self):
        self.__manager.moveDown([])
        self.assertEqual(
            list(self.__manager.keys()),
            self.names,
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveDown_1_no_effect(self):
        self.__manager.moveDown([self.names[-1]])
        self.assertEqual(
            list(self.__manager.keys()),
            self.names,
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveDown_many_no_effect(self):
        names = self.names
        self.__manager.moveDown([names[13], 'str88',
                                 names[11], names[12], '99'])
        self.assertEqual(
            list(self.__manager.keys()),
            self.names,
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveDown_1(self):
        names = self.names[:]
        n2 = names.pop(2)
        names.insert(3, n2)
        self.__manager.moveDown([n2])
        self.assertEqual(
            list(self.__manager.keys()),
            names,
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveDown_many(self):
        names = self.names
        self.__manager.moveDown(
            [names[0], names[2], 'str88', names[3],
             names[8], names[13], names[12], 'str99'])
        self.assertEqual(
            list(self.__manager.keys()),
            [names[1], names[0], names[4], names[2], names[3],
             names[5], names[6], names[7], names[9], names[8],
             names[10], names[11], names[12], names[13]],
            )

        # Make sure we still have the right items
        self.test_items()

    def test_moveDown_one_element_container(self):
        manager = RegistrationManager()
        name = manager.addRegistration('a')
        manager.moveDown([name])
        self.assertEqual(list(manager.items()), [(name, 'a')])

    #########################################################

class DummyRM(dict):
    def __iter__(self):
        for n in self.keys():
            yield n

class RegisterableContainerTests(placefulsetup.PlacefulSetup):

    def test_getRegistrationManager(self):
        sm = self.buildFolders(site=True)
        default = traverse(sm, 'default')
        self.assertEqual(default.getRegistrationManager(),
                         default['RegistrationManager'])
        default['xxx'] = RegistrationManager()
        del default['RegistrationManager']
        self.assertEqual(default.getRegistrationManager(),
                         default['xxx'])


#       Can't test empty because there's no way to make it empty.
##         del default[name]
##         self.assertRaises(Exception,
##                           default.getRegistrationManager)

    def test_cant_remove_last_cm(self):
        sm = self.buildFolders(site=True)
        default = traverse(sm, 'default')
        self.assertRaises(Exception,
                          default.__delitem__, 'registration')
        default['xxx'] = RegistrationManager()
        del default['RegistrationManager']


def test_suite():
    import sys
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
