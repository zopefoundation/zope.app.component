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
"""Service Directive Tests

$Id$
"""
import unittest
from cStringIO import StringIO

from zope.security.interfaces import Forbidden, Unauthorized

from zope.configuration.xmlconfig import testxmlconfig as xmlconfig, XMLConfig
from zope.configuration.config import ConfigurationConflictError
from zope.security.proxy import ProxyFactory
from zope.component.exceptions import ComponentLookupError

import zope.app.component
from zope.component import getService
from zope.app.tests.placelesssetup import PlacelessSetup


class ParticipationStub(object):

    def __init__(self, principal):
        self.principal = principal
        self.interaction = None


# TODO: tests for other directives needed

template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:test='http://www.zope.org/NS/Zope3/test'
   i18n_domain='zope'>
   %s
   </configure>"""

class Test(PlacelessSetup, unittest.TestCase):


    def setUp(self):
        super(Test, self).setUp()
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
        self.assertRaises(
            ConfigurationConflictError,
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
        self.assertRaises(ComponentLookupError, getService, "Foo")

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

        service = getService("Foo")
        self.assertEqual(service.foo(), "foo here")
        self.assertEqual(service.foobar(), "foobarred")
        self.assertEqual(service.bar(), "you shouldn't get this")

    def testServiceFactoryConfig(self):
        self.assertRaises(ComponentLookupError, getService, "Foo")

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

        service = getService("Foo")
        self.assertEqual(service.foo(), "foo here")
        self.assertEqual(service.foobar(), "foobarred")
        self.assertEqual(service.bar(), "you shouldn't get this")

    def testPublicProtectedServiceConfig(self):
        self.assertRaises(ComponentLookupError, getService, "Foo")

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

        service = getService("Foo")
        service = ProxyFactory(service) # simulate untrusted code!
        self.assertEqual(service.foo(), "foo here")
        self.assertEqual(service.foobar(), "foobarred")
        self.assertRaises(Forbidden, getattr, service, 'bar')

    def testProtectedServiceConfig(self):
        self.assertRaises(ComponentLookupError, getService, "Foo")

        xmlconfig(StringIO(template % (
            """
            <directives namespace="http://namespaces.zope.org/zope">
              <directive name="permission"
                 attributes="id title description"
                 handler="
              zope.app.security.metaconfigure.definePermission" />
            </directives>

            <permission id="zope.TestPermission" title="Test permission" />

            <serviceType id="Foo"
                         interface="
               zope.app.component.tests.service.IFooService"
               />
            <service
              serviceType="Foo"
              component="
              zope.app.component.tests.service.fooService"
              permission="zope.TestPermission"
              />
            """
            )))


        # Need to "log someone in" to turn on checks
        from zope.security.management import newInteraction, endInteraction
        endInteraction()
        newInteraction(ParticipationStub('someuser'))

        service = getService("Foo")
        service = ProxyFactory(service) # simulate untrusted code!

        self.assertRaises(Unauthorized, getattr, service, 'foo')
        self.assertRaises(Unauthorized, getattr, service, 'foobar')
        self.assertRaises(Forbidden, getattr, service, 'bar')


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
