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
"""ServiceManagerContainer implementation.

$Id$
"""

import zope.interface

from transaction import get_transaction
from zope.app.container.contained import Contained
from zope.app.site.interfaces import IPossibleSite, ISite
from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IServiceService
from zope.interface import implements

class ServiceManagerContainer(Contained):
    """Implement access to the service manager (++etc++site).

    This is a mix-in that implements the IPossibleSite
    interface; for example, it is used by the Folder implementation.
    """
    zope.interface.implements(IPossibleSite)

    __sm = None

    def getSiteManager(self):
        if self.__sm is not None:
            return self.__sm
        else:
            raise ComponentLookupError('no site manager defined')

    def setSiteManager(self, sm):
        if ISite.providedBy(self):
            raise TypeError("Already a site")

        if IServiceService.providedBy(sm):
            self.__sm = sm
            sm.__name__ = '++etc++site'
            sm.__parent__ = self
        else:
            raise ValueError('setSiteManager requires an IServiceService')

        zope.interface.directlyProvides(
            self, ISite,
            zope.interface.directlyProvidedBy(self))
