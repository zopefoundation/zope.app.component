##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Site-related BBB components

$Id$
"""
__docformat__ = "reStructuredText"
from zope.component.bbb.service import IService

import registration

class BBBSiteManager(object):

    def queryRegistrationsFor(self, cfg, default=None):
        return self.queryRegistrations(cfg.name, default)

    def queryRegistrations(self, name, default=None):
        """See INameRegistry"""
        return registration.RegistrationStack(self, name)

    def addSubsite(self, sub):
        return self.addSub(sub)

    def createRegistrationsFor(self, cfg):
        # Ignore
        pass

    def createRegistrations(self, name):
        # Ignore
        pass

    def listRegistrationNames(self):
        # Only used for services
        services = ['Utilities', 'Adapters']
        return [reg.name
                for reg in self.utilities.registrations()
                if reg.provided is IService] + services
        
    def queryActiveComponent(self, name, default=None):
        return self.queryLocalService(name, default)

    def getServiceDefinitions(self):
        gsm = zapi.getGlobalSiteManager()
        return gsm.getServiceDefinitions()

    def getService(self, name):
        return zapi.getUtility(IService, name, self)

    def queryLocalService(self, name, default=None):
        service = zapi.getUtility(IService, name, self)
        if zapi.getSiteManager(service) is not self:
            return default
        return service

    def getInterfaceFor(self, service_type):
        iface = [iface
                for name, iface in self.getServiceDefinitions()
                if name == service_type]
        return iface[0]

    def queryComponent(self, type=None, filter=None, all=0):
        # Ignore, hoping that noone uses this horrible method
        return []

