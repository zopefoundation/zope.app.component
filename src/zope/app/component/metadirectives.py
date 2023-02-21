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

# BBB
from zope.component.zcml import IBasicResourceInformation
from zope.component.zcml import IBasicViewInformation
from zope.component.zcml import IResourceDirective
from zope.component.zcml import IViewDirective
# BBB
from zope.security.metadirectives import IAllowSubdirective
from zope.security.metadirectives import IClassDirective
from zope.security.metadirectives import IFactorySubdirective
from zope.security.metadirectives import IImplementsSubdirective
from zope.security.metadirectives import IRequireSubdirective
