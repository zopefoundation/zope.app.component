##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

import unittest
from cStringIO import StringIO

from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.configuration.exceptions import ConfigurationError
from zope.app.security.exceptions import UndefinedPermissionError

from zope.proxy import getProxiedObject
from zope.security.proxy import getTestProxyItems

import zope.app.component
from zope.component.exceptions import ComponentLookupError
from zope.component import getView, queryView, queryResource
from zope.component import createObject
from zope.component import getDefaultViewName
from zope.component import getAdapter, queryAdapter
from zope.component import getNamedAdapter, queryNamedAdapter
from zope.component import getUtility, queryUtility

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component.tests.views import IV, IC, V1, VZMI, R1, RZMI
from zope.component.tests.request import Request
from zope.interface import implements


template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:test='http://www.zope.org/NS/Zope3/test'>
   %s
   </zopeConfigure>"""

class Ob:
    implements(IC)

def definePermissions():
    XMLConfig('meta.zcml', zope.app.component)()

class Test(PlacelessSetup, unittest.TestCase):

    # XXX: tests for other directives needed

    def setUp(self):
        PlacelessSetup.setUp(self)
        XMLConfig('metameta.zcml', zope.configuration)()
        XMLConfig('meta.zcml', zope.app.component)()
        XMLConfig('meta.zcml', zope.app.security)()

    def testAdapter(self):

        # Full import is critical!
        from zope.component.tests.components import Content, IApp, Comp

        self.assertEqual(queryAdapter(Content(), IV, None), None)

        xmlconfig(StringIO(template % (
            """
            <adapter
              factory="zope.component.tests.components.Comp"
              provides="zope.component.tests.components.IApp"
              for="zope.component.tests.components.IContent"
              />
            """
            )))

        self.assertEqual(getAdapter(Content(), IApp).__class__, Comp)

    def testNamedAdapter(self):


        # Full import is critical!
        from zope.component.tests.components import Content, IApp, Comp

        self.testAdapter()
        self.assertEqual(getAdapter(Content(), IApp).__class__, Comp)
        self.assertEqual(queryNamedAdapter(Content(), IV, 'test'),
                         None)

        xmlconfig(StringIO(template % (
            """
            <adapter
              factory="zope.component.tests.components.Comp"
              provides="zope.component.tests.components.IApp"
              for="zope.component.tests.components.IContent"
              name="test"
              />
            """
            )))

        self.assertEqual(getNamedAdapter(Content(), IApp, "test").__class__,
                         Comp)

    def testProtectedAdapter(self):

        # Full import is critical!
        from zope.component.tests.components import Content, IApp, Comp

        self.assertEqual(queryAdapter(Content(), IV, None), None)

        xmlconfig(StringIO(template % (
            """
            <adapter
              factory="zope.component.tests.components.Comp"
              provides="zope.component.tests.components.IApp"
              for="zope.component.tests.components.IContent"
              permission="zope.Public"
              />
            """
            )))

        adapter = getAdapter(Content(), IApp)
        items = [item[0] for item in getTestProxyItems(adapter)]
        self.assertEqual(items, ['a', 'f'])
        self.assertEqual(getProxiedObject(adapter).__class__, Comp)

    def testAdapterUndefinedPermission(self):
        config = StringIO(template % (
             """
             <adapter
              factory="zope.component.tests.components.Comp"
              provides="zope.component.tests.components.IApp"
              for="zope.component.tests.components.IContent"
              permission="UndefinedPermission"
              />
            """
            ))
        self.assertRaises(UndefinedPermissionError, xmlconfig, config,
                          testing=1)

    def testUtility(self):

        # Full import is critical!
        from zope.component.tests.components import IApp, comp

        self.assertEqual(queryUtility(None, IV, None), None)

        xmlconfig(StringIO(template % (
            """
            <utility
              component="zope.component.tests.components.comp"
              provides="zope.component.tests.components.IApp"
              />
            """
            )))

        self.assertEqual(getUtility(None, IApp), comp)

    def testNamedUtility(self):

        # Full import is critical!
        from zope.component.tests.components import IApp, comp

        self.testUtility()

        self.assertEqual(queryUtility(None, IV, None, name='test'), None)

        xmlconfig(StringIO(template % (
            """
            <utility
              component="zope.component.tests.components.comp"
              provides="zope.component.tests.components.IApp"
              name="test"
              />
            """
            )))

        self.assertEqual(getUtility(None, IApp, "test"), comp)

    def testUtilityFactory(self):

        # Full import is critical!
        from zope.component.tests.components import IApp, Comp

        self.assertEqual(queryUtility(None, IV, None), None)

        xmlconfig(StringIO(template % (
            """
            <utility
              factory="zope.component.tests.components.Comp"
              provides="zope.component.tests.components.IApp"
              />
            """
            )))

        self.assertEqual(getUtility(None, IApp).__class__, Comp)

    def testProtectedUtility(self):

        # Full import is critical!
        from zope.component.tests.components import IApp, comp

        self.assertEqual(queryUtility(None, IV, None), None)

        xmlconfig(StringIO(template % (
            """
            <utility
              component="zope.component.tests.components.comp"
              provides="zope.component.tests.components.IApp"
              permission="zope.Public"
              />
            """
            )))

        utility = getUtility(None, IApp)
        items = [item[0] for item in getTestProxyItems(utility)]
        self.assertEqual(items, ['a', 'f'])
        self.assertEqual(getProxiedObject(utility), comp)

    def testUtilityUndefinedPermission(self):
        config = StringIO(template % (
             """
             <utility
              component="zope.component.tests.components.comp"
              provides="zope.component.tests.components.IApp"
              permission="UndefinedPermission"
              />
            """
            ))
        self.assertRaises(UndefinedPermissionError, xmlconfig, config,
                          testing=1)


    def testView(self):

        ob = Ob()
        self.assertEqual(queryView(ob, 'test', Request(IV), None), None)

        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  type="zope.component.tests.views.IV"/>
            """
            ))

        self.assertEqual(queryView(ob, 'test', Request(IV), None).__class__,
                         V1)

    def testInterfaceProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  type="zope.component.tests.views.IV"
                  permission="zope.Public"
              allowed_interface="zope.component.tests.views.IV"
                  />
            """
            ))

        v = getView(Ob(), 'test', Request(IV))
        self.assertEqual(v.index(), 'V1 here')
        self.assertRaises(Exception, getattr, v, 'action')

    def testAttributeProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  type="zope.component.tests.views.IV"
                  permission="zope.Public"
                  allowed_attributes="action"
                  />
            """
            ))

        v = getView(Ob(), 'test', Request(IV))
        self.assertEqual(v.action(), 'done')
        self.assertRaises(Exception, getattr, v, 'index')

    def testInterfaceAndAttributeProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  type="zope.component.tests.views.IV"
                  permission="zope.Public"
                  allowed_attributes="action"
              allowed_interface="zope.component.tests.views.IV"
                  />
            """
            ))

        v = getView(Ob(), 'test', Request(IV))
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testDuplicatedInterfaceAndAttributeProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  type="zope.component.tests.views.IV"
                  permission="zope.Public"
                  allowed_attributes="action index"
              allowed_interface="zope.component.tests.views.IV"
                  />
            """
            ))

        v = getView(Ob(), 'test', Request(IV))
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testIncompleteProtectedViewNoPermission(self):
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(template %
            """
            <view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  type="zope.component.tests.views.IV"
                  allowed_attributes="action index"
                  />
            """
            ))

    def testViewUndefinedPermission(self):
        config = StringIO(template % (
            """
            <view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  type="zope.component.tests.views.IV"
                  permission="UndefinedPermission"
                  allowed_attributes="action index"
              allowed_interface="zope.component.tests.views.IV"
                  />
            """
            ))
        self.assertRaises(UndefinedPermissionError, xmlconfig, config,
                          testing=1)



    def testDefaultView(self):

        ob = Ob()
        self.assertEqual(queryView(ob, 'test', Request(IV), None), None)

        xmlconfig(StringIO(template % (
            """
            <defaultView name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  type="zope.component.tests.views.IV"/>
            """
            )))

        self.assertEqual(queryView(ob, 'test', Request(IV), None).__class__,
                         V1)
        self.assertEqual(getDefaultViewName(ob, Request(IV)), 'test')

    def testDefaultViewOnly(self):

        ob = Ob()
        self.assertEqual(queryView(ob, 'test', Request(IV), None), None)

        xmlconfig(StringIO(template % (
            """
            <defaultView name="test"
                  for="zope.component.tests.views.IC"
                  type="zope.component.tests.views.IV"/>
            """
            )))

        self.assertEqual(queryView(ob, 'test', Request(IV), None), None)
        self.assertEqual(getDefaultViewName(ob, Request(IV)), 'test')

    def testSkinView(self):

        ob = Ob()
        self.assertEqual(queryView(ob, 'test', Request(IV), None), None)

        xmlconfig(StringIO(template % (
            """
            <skin name="zmi" layers="zmi default"
                  type="zope.component.tests.views.IV" />
            <view name="test"
                  factory="zope.component.tests.views.VZMI"
                  layer="zmi"
                  for="zope.component.tests.views.IC"
                  type="zope.component.tests.views.IV"/>
            <view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  type="zope.component.tests.views.IV"/>
            """
            )))

        self.assertEqual(queryView(ob, 'test', Request(IV), None).__class__,
                         V1)
        self.assertEqual(
            queryView(ob, 'test', Request(IV, 'zmi'), None).__class__,
            VZMI)

    def testResource(self):

        ob = Ob()
        self.assertEqual(queryResource(ob, 'test', Request(IV), None), None)
        xmlconfig(StringIO(template % (
            """
            <resource name="test"
                  factory="zope.component.tests.views.R1"
                  type="zope.component.tests.views.IV"/>
            """
            )))

        self.assertEqual(queryResource(ob, 'test', Request(IV), None
                                       ).__class__,
                         R1)

    def testResourceUndefinedPermission(self):

        config = StringIO(template % (
            """
            <resource name="test"
                  factory="zope.component.tests.views.R1"
                  type="zope.component.tests.views.IV"
                  permission="UndefinedPermission"/>
            """
            ))
        self.assertRaises(UndefinedPermissionError, xmlconfig, config,
                          testing=1)


    def testSkinResource(self):

        ob = Ob()
        self.assertEqual(queryResource(ob, 'test', Request(IV), None), None)

        xmlconfig(StringIO(template % (
            """
            <skin name="zmi" layers="zmi default"
                  type="zope.component.tests.views.IV" />
            <resource name="test"
                  factory="zope.component.tests.views.RZMI"
                  layer="zmi"
                  type="zope.component.tests.views.IV"/>
            <resource name="test"
                  factory="zope.component.tests.views.R1"
                  type="zope.component.tests.views.IV"/>
            """
            )))

        self.assertEqual(
            queryResource(ob, 'test', Request(IV), None).__class__,
            R1)
        self.assertEqual(
            queryResource(ob, 'test', Request(IV, 'zmi'), None).__class__,
            RZMI)

    def testFactory(self):

        self.assertRaises(ComponentLookupError, createObject, None, 'foo')

        xmlconfig(StringIO(template % (
            """
            <factory
               id="foo"
               component="zope.component.tests.factory.f"
               />
            <factory
               component="zope.component.tests.factory.f"
               />
            """
            )))

        from zope.component.tests.factory import X
        self.assertEqual(createObject(None, 'foo').__class__, X)
        self.assertEqual(createObject(
            None,
            'zope.component.tests.factory.f').__class__, X)


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)
if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
