##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Unit test logic for setting up and tearing down basic infrastructure

$Id: placelesssetup.py,v 1.4 2003/02/11 15:59:40 sidnei Exp $
"""

from zope.component import getServiceManager
from zope.component.servicenames import Interfaces
from zope.app.component.globalinterfaceservice import IInterfaceService
from zope.app.component.globalinterfaceservice import interfaceService

class PlacelessSetup:

    def setUp(self):

        sm = getServiceManager(None)
        defineService = sm.defineService
        provideService = sm.provideService

        defineService(Interfaces, IInterfaceService)
        provideService(Interfaces, interfaceService)
