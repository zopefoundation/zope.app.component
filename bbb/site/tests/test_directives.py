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
"""Local Service Directive Tests

$Id: tests.py 27873 2004-10-10 07:24:06Z srichter $
"""
import unittest
from StringIO import StringIO

from zope.configuration.xmlconfig import xmlconfig, XMLConfig

import zope.app.security
import zope.app.site
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.site.interfaces import ISimpleService

def configfile(s):
    return StringIO("""<configure
      xmlns='http://namespaces.zope.org/zope'
      i18n_domain='zope'>
      %s
      </configure>
      """ % s)

class ServiceStub(object):
    pass

class TestLocalServiceDirective(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(TestLocalServiceDirective, self).setUp()
        XMLConfig('meta.zcml', zope.app.component)()
        XMLConfig('meta.zcml', zope.app.site)()

    def testDirective(self):
        f = configfile('''
        <localService
            class="zope.app.site.tests.test_directives.ServiceStub">
        </localService>
        ''')
        xmlconfig(f)
        self.assert_(ISimpleService.implementedBy(ServiceStub))
    

def test_suite():
    return unittest.makeSuite(TestLocalServiceDirective)

if __name__ == '__main__':
    unittest.main(default='test_suite')
