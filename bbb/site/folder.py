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
"""A site management folder contains components and component registrations.

$Id$
"""
from zope.interface import implements
from zope.app.container.btree import BTreeContainer
from zope.app.filerepresentation.interfaces import IDirectoryFactory
from zope.app.registration.registration import RegisterableContainer
from zope.app.traversing.api import getPath
from zope.app.container.contained import setitem

from zope.app.site.interfaces import ISiteManagementFolders
from zope.app.site.interfaces import ISiteManagementFolder
from zope.app.site.interfaces import IComponentManager

class SiteManagementFolder(RegisterableContainer, BTreeContainer):
    implements(ISiteManagementFolder)

class SMFolderFactory(object):
    implements(IDirectoryFactory)

    def __init__(self, context):
        self.context = context

    def __call__(self, name):
        return SiteManagementFolder()

class SiteManagementFolders(BTreeContainer):
    pass 

import sys

sys.modules['zope.app.services.package'
            ] = sys.modules['zope.app.site.folder']
