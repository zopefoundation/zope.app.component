##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Backwards compatibility module.

The real interfaces are defined in zope.site.interfaces.
$Id$
"""

import zope.deferredimport

from zope.site.interfaces import (INewLocalSite,
                                  NewLocalSite,
                                  ILocalSiteManager,
                                  ISiteManagementFolder)

zope.deferredimport.deprecatedFrom(
    "Moved to zope.location.interfaces. Importing from here will stop working in Zope 3.6",
    "zope.location.interfaces",
    "ISite", "IPossibleSite")
                    
