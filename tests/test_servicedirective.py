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
import sys
import os
from cStringIO import StringIO

from zope.exceptions import Forbidden, Unauthorized

from zope.configuration.xmlconfig import testxmlconfig as xmlconfig, XMLConfig
from zope.configuration.exceptions import ConfigurationError

from zope.security.proxy \
     import getTestProxyItems, getObject as proxiedObject, ProxyFactory

from zope.component.exceptions import ComponentLookupError

from zope.app.component.tests.service import IFooService, FooService

import zope.app.component
from zope.component import getService
from zope.app.tests.placelesssetup import PlacelessSetup


template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:test='http://www.zope.org/NS/Zope3/test'>
   %s
   </zopeConfigure>"""


class Test(PlacelessSetup, unittest.TestCase):

    # XXX: tests for other directives needed

    def setUp(self):
        PlacelessSetup.setUp(self)
        XMLConfig('meta.zcml', zope.app.component)()

    def testServiceConfigNoType(self):
        from zope.component.service \
             import UndefinedService
        self.assertRaises(
            UndefinedService,
            xmlconfig,
            StringIO(template % (
            """
            <service
              serviceType="Foo"
              component="
              zope.app.component.tests.service.fooService"
              />
            """
            )))

    def testDuplicateServiceConfig(self):
        from zope.configuration.xmlconfig \
             import ZopeConflictingConfigurationError
        self.assertRaises(
            ZopeConflictingConfigurationError,
            xmlconfig,
            StringIO(template % (
            """
            <serviceType id="Foo"
                         interface="
               zope.app.component.tests.service.IFooService"
               />
            <service
              serviceType="Foo"
              component="
              zope.app.component.tests.service.fooService"
              />
            <service
              serviceType="Foo"
              component="
              zope.app.component.tests.service.foo2"
              />
            """
            )))

    def testServiceConfig(self):
        self.assertRaises(ComponentLookupError, getService, None, "Foo")

        xmlconfig(StringIO(template % (
            """
            <serviceType id="Foo"
                         interface="
               zope.app.component.tests.service.IFooService"
               />
            <service
              serviceType="Foo"
              component="
              zope.app.component.tests.service.fooService"
              />
            """
            )))

        service = getService(None, "Foo")
        self.assertEqual(service.foo(), "foo here")
        self.assertEqual(service.foobar(), "foobarred")
        self.assertEqual(service.bar(), "you shouldn't get this")

    def testServiceFactoryConfig(self):
        self.assertRaises(ComponentLookupError, getService, None, "Foo")

        xmlconfig(StringIO(template % (
            """
            <serviceType id="Foo"
                         interface="
               zope.app.component.tests.service.IFooService"
               />
            <service
              serviceType="Foo"
              factory="
              zope.app.component.tests.service.FooService"
              />
            """
            )))

        service = getService(None, "Foo")
        self.assertEqual(service.foo(), "foo here")
        self.assertEqual(service.foobar(), "foobarred")
        self.assertEqual(service.bar(), "you shouldn't get this")

    def testPublicProtectedServiceConfig(self):
        self.assertRaises(ComponentLookupError, getService, None, "Foo")

        xmlconfig(StringIO(template % (
            """
            <serviceType id="Foo"
                         interface="
               zope.app.component.tests.service.IFooService"
               />
            <service
              serviceType="Foo"
              component="
              zope.app.component.tests.service.fooService"
              permission="zope.Public"
              />
            """
            )))

        service = getService(None, "Foo")
        service = ProxyFactory(service) # simulate untrusted code!
        self.assertEqual(service.foo(), "foo here")
        self.assertEqual(service.foobar(), "foobarred")
        self.assertRaises(Forbidden, getattr, service, 'bar')

    def testProtectedServiceConfig(self):
        self.assertRaises(ComponentLookupError, getService, None, "Foo")

        xmlconfig(StringIO(template % (
            """
            <directives namespace="http://namespaces.zope.org/zope">
              <directive name="permission"
                 attributes="id title description"
                 handler="
              zope.app.security.registries.metaconfigure.definePermission" />
            </directives>

            <permission id="XXX" title="xxx" />

            <serviceType id="Foo"
                         interface="
               zope.app.component.tests.service.IFooService"
               />
            <service
              serviceType="Foo"
              component="
              zope.app.component.tests.service.fooService"
              permission="XXX"
              />
            """
            )))


        # Need to "log someone in" to turn on checks
        from zope.security.securitymanagement import newSecurityManager
        newSecurityManager('someuser')

        service = getService(None, "Foo")
        service = ProxyFactory(service) # simulate untrusted code!

        self.assertRaises(Unauthorized, getattr, service, 'foo')
        self.assertRaises(Unauthorized, getattr, service, 'foobar')
        self.assertRaises(Forbidden, getattr, service, 'bar')



def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)
if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
