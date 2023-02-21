##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""This module here is for backwards compatibility.

The real public API is now zope.site
"""
# on the side of caution for backwards compatibility we
# import everything defined
from zope.component.hooks import setSite
from zope.site.site import LocalSiteManager
from zope.site.site import SiteManagementFolder
from zope.site.site import SiteManagerAdapter
from zope.site.site import SiteManagerContainer
from zope.site.site import SMFolderFactory
from zope.site.site import _findNextSiteManager
from zope.site.site import _LocalAdapterRegistry
from zope.site.site import changeSiteConfigurationAfterMove  # BBB
from zope.site.site import clearSite
from zope.site.site import clearThreadSiteSubscriber
from zope.site.site import threadSiteSubscriber
