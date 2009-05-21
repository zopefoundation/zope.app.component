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

import zope.deferredimport
import zope.security

# BBB
zope.deferredimport.deprecatedFrom(
    "Schemas for the ``class`` directive and its subdirectives are now "
    "moved to zope.security.metadirectives. Imports from here are "
    "deprecated and will be removed in Zope 3.6",

    'zope.security.metadirectives',

    'IClassDirective',
    'IImplementsSubdirective',
    'IRequireSubdirective',
    'IAllowSubdirective',
    'IFactorySubdirective',
)

# BBB
from zope.component.zcml import (IBasicViewInformation,
                                 IBasicResourceInformation,
                                 IViewDirective,
                                 IResourceDirective)
