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
"""

Revision information:
$Id: test_servicemanagercontainer.py,v 1.6 2003/05/27 14:18:12 jim Exp $
"""

from unittest import TestCase, main, makeSuite
from zope.component.interfaces import IServiceService
from zope.app.interfaces.services.service import IServiceManagerContainer
from zope.component.exceptions import ComponentLookupError
from zope.interface.verify import verifyObject
from zope.context import getbaseobject

class ServiceManager:

    __implements__ =  IServiceService

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

class BaseTestServiceManagerContainer:

    """This test is for objects that don't have service managers by
    default and that always give back the service manager they were
    given.


    Subclasses need to define a method, 'makeTestObject', that takes no
    arguments and that returns a new service manager
    container that has no service manager."""

    def testIServiceManagerContainerVerify(self):
        verifyObject(IServiceManagerContainer, self.makeTestObject())

    def testHas(self):
        smc=self.makeTestObject()
        self.failIf(smc.hasServiceManager())
        smc.setServiceManager(ServiceManager())
        self.failUnless(smc.hasServiceManager())

    def testGet(self):
        smc=self.makeTestObject()
        # since the managers are now wrapped, need to look at base object
        self.failUnless(getbaseobject(smc.queryServiceManager()) is None)
        self.assertRaises(ComponentLookupError, smc.getServiceManager)
        sm=ServiceManager()
        smc.setServiceManager(sm)
        self.failUnless(getbaseobject(smc.getServiceManager()) is sm)
        self.failUnless(getbaseobject(smc.queryServiceManager(self)) is sm)

    def testSet(self):
        smc=self.makeTestObject()
        self.assertRaises(Exception, smc.setServiceManager, self)



class Test(BaseTestServiceManagerContainer, TestCase):
    def makeTestObject(self):
        from zope.app.services.servicecontainer \
             import ServiceManagerContainer
        return ServiceManagerContainer()


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
