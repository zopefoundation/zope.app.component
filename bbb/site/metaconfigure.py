##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Local Service Directive

$Id$
"""
__docformat__ = "reStructuredText"
from zope.interface import classImplements
from zope.app.component.contentdirective import ContentDirective

from interfaces import ISimpleService


class LocalServiceDirective(ContentDirective):

    def __init__(self, _context, class_):
        if not ISimpleService.implementedBy(class_):
            classImplements(class_, ISimpleService)
        super(LocalServiceDirective, self).__init__(_context, class_)
