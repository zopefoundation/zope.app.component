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
""" Test handler for 'factory' subdirective of 'content' directive """

import unittest
from cStringIO import StringIO

from zope.configuration.xmlconfig import xmlconfig
from zope.configuration.xmlconfig import XMLConfig
from zope.app.services.servicenames import Factories
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.security.management import newSecurityManager, system_user

import zope.configuration
import zope.app.security
import zope.app.component

from zope.app.component.tests.exampleclass import ExampleClass

def configfile(s):
    return StringIO("""<configure
      xmlns='http://namespaces.zope.org/zope'
      i18n_domain='zope'>
      %s
      </configure>
      """ % s)

class Test(PlacelessSetup, unittest.TestCase):
    def setUp(self):
        super(Test, self).setUp()
        newSecurityManager(system_user)
        XMLConfig('meta.zcml', zope.app.component)()
        XMLConfig('meta.zcml', zope.app.security)()

    def testFactory(self):
        from zope.component import getService
        from zope.proxy import removeAllProxies
        f = configfile("""
<permission id="zope.Foo" title="Zope Foo Permission" />
<content class="zope.app.component.tests.exampleclass.ExampleClass">
    <factory
      id="Example"
      permission="zope.Foo"
      title="Example content"
      description="Example description"
       />
</content>
                       """)
        xmlconfig(f)
        obj = getService(None, Factories).createObject('Example')
        obj = removeAllProxies(obj)
        self.failUnless(isinstance(obj, ExampleClass))

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
