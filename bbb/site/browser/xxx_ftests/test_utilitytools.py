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
"""Utility Tools Functional Tests

$Id$
"""
import unittest

from zope.app import zapi
from zope.i18n.interfaces import ITranslationDomain
from zope.app.registration.interfaces import ActiveStatus, RegisteredStatus
from zope.app.testing.functional import BrowserTestCase

class TestUtilityTool(BrowserTestCase):

    def testContent(self):
        path = '/++etc++site/@@manageITranslationDomainTool.html'
        # create the view
        response = self.publish(path, basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)

        body = response.getBody()

        # test for broken links
        self.checkForBrokenLinks(body, path, basic='mgr:mgrpw')

        # We can't really test more here, since we do not know what type of
        # utilities will registered as tools.

    def testAdd(self):
        path = '/++etc++site/@@AddITranslationDomainTool'
        # create the view
        response = self.publish(path, basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)

        body = response.getBody()

        # test for broken links
        self.checkForBrokenLinks(body, path, basic='mgr:mgrpw')

        # attempt to add something
        response = self.publish(
            path+'/action.html', basic='mgr:mgrpw',
            form={'type_name':
                  'BrowserAdd__'
                  'zope.app.i18n.translationdomain.TranslationDomain',
                  'id': 'zope',
                  'add': 'Add'})

        root = self.getRootFolder()
        tools = zapi.traverse(root, '/++etc++site/tools')
        self.assert_('zope' in tools.keys())

        # Make sure that the new utility has a parent and a name
        zope = zapi.getUtility(ITranslationDomain, 'zope', context=tools)
        self.assertEqual(zapi.getParent(zope), tools)
        self.assertEqual(zapi.getName(zope), 'zope')
        

    def testDelete(self):
        path = '/++etc++site/@@AddITranslationDomainTool'
        # create the view
        response = self.publish(path, basic='mgr:mgrpw')

        self.publish(
            path + '/action.html',
            basic='mgr:mgrpw',
            form={'type_name':
                  'BrowserAdd__'
                  'zope.app.i18n.translationdomain.TranslationDomain',
                  'id': 'zope',
                  'add': 'Add'})

        response = self.publish(
            '/++etc++site/@@manageITranslationDomainTool.html',
            basic='mgr:mgrpw',
            form={'selected': ['zope'],
                  'DELETE': 'Delete'})

        root = self.getRootFolder()
        tools = zapi.traverse(root, '/++etc++site/tools')
        self.assert_('zope' not in tools.keys())

    def testRename(self):
        path = '/++etc++site/@@AddITranslationDomainTool'
        # create the view
        response = self.publish(path, basic='mgr:mgrpw')

        self.publish(
            path + '/action.html',
            basic='mgr:mgrpw',
            form={'type_name':
                  'BrowserAdd__'
                  'zope.app.i18n.translationdomain.TranslationDomain',
                  'id': 'zope',
                  'add': 'Add'})

        response = self.publish(
            '/++etc++site/@@manageITranslationDomainTool.html',
            basic='mgr:mgrpw',
            form={'selected': ['zope'],
                  'old_names': ['zope'],
                  'new_names': ['newzope'],
                  'APPLY_RENAME': 'Rename'})

        root = self.getRootFolder()
        util = zapi.queryUtility(ITranslationDomain, 'newzope', context=root)
        self.assert_(util is not None)

    def testDeactivate(self):
        path = '/++etc++site/@@AddITranslationDomainTool'
        # create the view
        response = self.publish(path, basic='mgr:mgrpw')

        self.publish(
            path + '/action.html',
            basic='mgr:mgrpw',
            form={'type_name':
                  'BrowserAdd__'
                  'zope.app.i18n.translationdomain.TranslationDomain',
                  'id': 'zope',
                  'add': 'Add'})

        response = self.publish(
            '/++etc++site/@@manageITranslationDomainTool.html',
            basic='mgr:mgrpw',
            form={'selected': ['zope'],
                  'DEACTIVATE': 'Rename'})

        root = self.getRootFolder()
        utils = zapi.getService('Utilities', root)
        reg = utils.queryRegistrations('zope', ITranslationDomain)

        for info in reg.info():
            self.assert_(info['registration'].status == RegisteredStatus)
            
    def testActivate(self):
        path = '/++etc++site/@@AddITranslationDomainTool'
        # create the view
        response = self.publish(path, basic='mgr:mgrpw')

        self.publish(
            path + '/action.html',
            basic='mgr:mgrpw',
            form={'type_name':
                  'BrowserAdd__'
                  'zope.app.i18n.translationdomain.TranslationDomain',
                  'id': 'zope',
                  'add': 'Add'})

        response = self.publish(
            '/++etc++site/@@manageITranslationDomainTool.html',
            basic='mgr:mgrpw',
            form={'selected': ['zope'],
                  'DEACTIVATE': 'Rename'})

        response = self.publish(
            '/++etc++site/@@manageITranslationDomainTool.html',
            basic='mgr:mgrpw',
            form={'selected': ['zope'],
                  'ACTIVATE': 'Rename'})

        root = self.getRootFolder()
        utils = zapi.getService('Utilities', root)
        reg = utils.queryRegistrations('zope', ITranslationDomain)

        for info in reg.info():
            self.assert_(info['registration'].status == ActiveStatus)

        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUtilityTool))
    return suite

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
