#############################################################################
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
"""Backwards compatibility: moved this module to
`zope.security.metaconfigure`.

$Id$
"""
__docformat__ = 'restructuredtext'

import zope.deferredimport

zope.deferredimport.deprecated(
    "The ``class`` directive implementation was moved to "
    "zope.security.metaconfigure. This import will stop "
    "working in Zope 3.6",
    ClassDirective = 'zope.security.metaconfigure:ClassDirective'
    )
