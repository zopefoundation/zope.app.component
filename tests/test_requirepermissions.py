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
"""Test handler for 'require' subdirective of 'content' directive

$Id$
"""
from cStringIO import StringIO
import unittest

import zope.app.component
import zope.app.security

from zope.app.component.interface import queryInterface
from zope.app.component.tests import module
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.security.checker import selectChecker
from zope.interface import implements

# So we can use config parser to exercise protectClass stuff.
from zope.configuration.xmlconfig import XMLConfig
from zope.configuration.xmlconfig import xmlconfig, ZopeXMLConfigurationError

PREFIX = module.__name__ + '.'

def defineDirectives():
    XMLConfig('meta.zcml', zope.app.component)()
    XMLConfig('meta.zcml', zope.app.security)()
    xmlconfig(StringIO("""<configure
        xmlns='http://namespaces.zope.org/zope'
        i18n_domain='zope'>
       <permission id="zope.Extravagant" title="extravagant" />
       <permission id="zope.Paltry" title="paltry" />
    </configure>"""))

NOTSET = []

P1 = "zope.Extravagant"
P2 = "zope.Paltry"

class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(Test, self).setUp()
        defineDirectives()

        class B(object):
            def m1(self):
                return "m1"
            def m2(self):
                return "m2"
        class C(B):
            implements(module.I)
            def m3(self):
                return "m3"
            def m4(self):
                return "m4"
        module.test_base = B
        module.test_class = C
        module.test_instance = C()
        self.assertState()

    def tearDown(self):
        PlacelessSetup.tearDown(self)
        module.test_class = None

    def assertState(self, m1P=NOTSET, m2P=NOTSET, m3P=NOTSET):
        "Verify that class, instance, and methods have expected permissions."

        from zope.security.checker import selectChecker

        checker = selectChecker(module.test_instance)
        self.assertEqual(checker.permission_id('m1'), (m1P or None))
        self.assertEqual(checker.permission_id('m2'), (m2P or None))
        self.assertEqual(checker.permission_id('m3'), (m3P or None))

    def assertDeclaration(self, declaration, **state):
        apply_declaration(module.template_bracket % declaration)
        self.assertState(**state)

    # "testSimple*" exercises tags that do NOT have children.  This mode
    # inherently sets the instances as well as the class attributes.

    def testSimpleMethodsPlural(self):
        declaration = ("""<content class="%s">
                            <require
                                permission="%s"
                                attributes="m1 m3"/>
                          </content>"""
                       % (PREFIX+"test_class", P1))
        self.assertDeclaration(declaration, m1P=P1, m3P=P1)

    def assertSetattrState(self, m1P=NOTSET, m2P=NOTSET, m3P=NOTSET):
        "Verify that class, instance, and methods have expected permissions."

        from zope.security.checker import selectChecker

        checker = selectChecker(module.test_instance)
        self.assertEqual(checker.setattr_permission_id('m1'), (m1P or None))
        self.assertEqual(checker.setattr_permission_id('m2'), (m2P or None))
        self.assertEqual(checker.setattr_permission_id('m3'), (m3P or None))

    def assertSetattrDeclaration(self, declaration, **state):
        self.assertSetattrState(**state)

    def test_set_attributes(self):
        declaration = ("""<content class="%s">
                            <require
                                permission="%s"
                                set_attributes="m1 m3"/>
                          </content>"""
                       % (PREFIX+"test_class", P1))
        apply_declaration(module.template_bracket % declaration)
        checker = selectChecker(module.test_instance)
        self.assertEqual(checker.setattr_permission_id('m1'), P1)
        self.assertEqual(checker.setattr_permission_id('m2'), None)
        self.assertEqual(checker.setattr_permission_id('m3'), P1)

    def test_set_schema(self):

        self.assertEqual(queryInterface(PREFIX+"S"), None)

        declaration = ("""<content class="%s">
                            <require
                                permission="%s"
                                set_schema="%s"/>
                          </content>"""
                       % (PREFIX+"test_class", P1, PREFIX+"S"))
        apply_declaration(module.template_bracket % declaration)

        self.assertEqual(queryInterface(PREFIX+"S"), module.S)


        checker = selectChecker(module.test_instance)
        self.assertEqual(checker.setattr_permission_id('m1'), None)
        self.assertEqual(checker.setattr_permission_id('m2'), None)
        self.assertEqual(checker.setattr_permission_id('m3'), None)
        self.assertEqual(checker.setattr_permission_id('foo'), P1)
        self.assertEqual(checker.setattr_permission_id('bar'), P1)
        self.assertEqual(checker.setattr_permission_id('baro'), None)

    def test_multiple_set_schema(self):

        self.assertEqual(queryInterface(PREFIX+"S"), None)
        self.assertEqual(queryInterface(PREFIX+"S2"), None)

        declaration = ("""<content class="%s">
                            <require
                                permission="%s"
                                set_schema="%s %s"/>
                          </content>"""
                       % (PREFIX+"test_class", P1, PREFIX+"S", PREFIX+"S2"))
        apply_declaration(module.template_bracket % declaration)

        self.assertEqual(queryInterface(PREFIX+"S"), module.S)
        self.assertEqual(queryInterface(PREFIX+"S2"), module.S2)


        checker = selectChecker(module.test_instance)
        self.assertEqual(checker.setattr_permission_id('m1'), None)
        self.assertEqual(checker.setattr_permission_id('m2'), None)
        self.assertEqual(checker.setattr_permission_id('m3'), None)
        self.assertEqual(checker.setattr_permission_id('foo'), P1)
        self.assertEqual(checker.setattr_permission_id('bar'), P1)
        self.assertEqual(checker.setattr_permission_id('foo2'), P1)
        self.assertEqual(checker.setattr_permission_id('bar2'), P1)
        self.assertEqual(checker.setattr_permission_id('baro'), None)

    def testSimpleInterface(self):

        self.assertEqual(queryInterface(PREFIX+"I"), None)

        declaration = ("""<content class="%s">
                            <require
                                permission="%s"
                                interface="%s"/>
                          </content>"""
                       % (PREFIX+"test_class", P1, PREFIX+"I"))
        # m1 and m2 are in the interface, so should be set, and m3 should not:
        self.assertDeclaration(declaration, m1P=P1, m2P=P1)

        # Make sure we know about the interfaces
        self.assertEqual(queryInterface(PREFIX+"I"), module.I)
        

    def testMultipleInterface(self):

        self.assertEqual(queryInterface(PREFIX+"I3"), None)
        self.assertEqual(queryInterface(PREFIX+"I4"), None)

        declaration = ("""<content class="%s">
                            <require
                                permission="%s"
                                interface="  %s
                                             %s  "/>
                          </content>"""
                       % (PREFIX+"test_class", P1, PREFIX+"I3", PREFIX+"I4"))
        self.assertDeclaration(declaration, m3P=P1, m2P=P1)

        # Make sure we know about the interfaces
        self.assertEqual(queryInterface(PREFIX+"I3"), module.I3)
        self.assertEqual(queryInterface(PREFIX+"I4"), module.I4)

    # "testComposite*" exercises tags that DO have children.
    # "testComposite*TopPerm" exercises tags with permission in containing tag.
    # "testComposite*ElementPerm" exercises tags w/permission in children.

    def testCompositeNoPerm(self):
        # Establish rejection of declarations lacking a permission spec.
        declaration = ("""<content class="%s">
                            <require
                                attributes="m1"/>
                          </content>"""
                       % (PREFIX+"test_class"))
        self.assertRaises(ZopeXMLConfigurationError,
                          self.assertDeclaration,
                          declaration)



    def testCompositeMethodsPluralElementPerm(self):
        declaration = ("""<content class="%s">
                            <require
                                permission="%s"
                                attributes="m1 m3"/>
                          </content>"""
                       % (PREFIX+"test_class", P1))
        self.assertDeclaration(declaration,
                               m1P=P1, m3P=P1)

    def testCompositeInterfaceTopPerm(self):
        declaration = ("""<content class="%s">
                            <require
                                permission="%s"
                                interface="%s"/>
                          </content>"""
                       % (PREFIX+"test_class", P1, PREFIX+"I"))
        self.assertDeclaration(declaration,
                               m1P=P1, m2P=P1)


    def testSubInterfaces(self):
        declaration = ("""<content class="%s">
                            <require
                                permission="%s"
                                interface="%s"/>
                          </content>"""
                       % (PREFIX+"test_class", P1, PREFIX+"I2"))
        # m1 and m2 are in the interface, so should be set, and m3 should not:
        self.assertDeclaration(declaration, m1P=P1, m2P=P1)


    def testMimicOnly(self):
        declaration = ("""<content class="%s">
                            <require
                                permission="%s"
                                attributes="m1 m2"/>
                          </content>
                          <content class="%s">
                            <require like_class="%s" />
                          </content>
                          """ % (PREFIX+"test_base", P1,
                PREFIX+"test_class", PREFIX+"test_base"))
        # m1 and m2 are in the interface, so should be set, and m3 should not:
        self.assertDeclaration(declaration,
                               m1P=P1, m2P=P1)


    def testMimicAsDefault(self):
        declaration = ("""<content class="%s">
                            <require
                                permission="%s"
                                attributes="m1 m2"/>
                          </content>
                          <content class="%s">
                            <require like_class="%s" />
                            <require
                                permission="%s"
                                attributes="m2 m3"/>
                          </content>
                          """ % (PREFIX+"test_base", P1,
                PREFIX+"test_class", PREFIX+"test_base", P2))

        # m1 and m2 are in the interface, so should be set, and m3 should not:
        self.assertDeclaration(declaration,
                               m1P=P1, m2P=P2, m3P=P2)


def apply_declaration(declaration):
    """Apply the xmlconfig machinery."""
    return xmlconfig(StringIO(declaration))

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
