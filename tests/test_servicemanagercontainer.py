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
"""Service Manager Container Tests

$Id$
"""
from unittest import TestCase, main, makeSuite
from zope.component.interfaces import IServiceService
from zope.app.site.interfaces import IPossibleSite, ISite
from zope.component.exceptions import ComponentLookupError
from zope.interface.verify import verifyObject
from zope.interface import implements

class ServiceManager(object):

    implements(IServiceService)

    ############################################################
    # Implementation methods for interface
    # IServiceService.

    def getService(self, object, name):
        '''See interface IServiceService'''
        raise ComponentLookupError(name)

    def getServiceDefinitions(self):
        '''See interface IServiceService'''
        return ()

    #
    ############################################################

class BaseTestServiceManagerContainer(object):

    """This test is for objects that don't have service managers by
    default and that always give back the service manager they were
    given.


    Subclasses need to define a method, 'makeTestObject', that takes no
    arguments and that returns a new service manager
    container that has no service manager."""

    def test_IPossibleSite_verify(self):
        verifyObject(IPossibleSite, self.makeTestObject())

    def test_get_and_set(self):
        smc = self.makeTestObject()
        self.failIf(ISite.providedBy(smc))
        sm = ServiceManager()
        smc.setSiteManager(sm)
        self.failUnless(ISite.providedBy(smc))
        self.failUnless(smc.getSiteManager() is sm)
        verifyObject(ISite, smc)

    def test_set_w_bogus_value(self):
        smc=self.makeTestObject()
        self.assertRaises(Exception, smc.setSiteManager, self)



class Test(BaseTestServiceManagerContainer, TestCase):
    def makeTestObject(self):
        from zope.app.site.servicecontainer import ServiceManagerContainer
        return ServiceManagerContainer()


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
