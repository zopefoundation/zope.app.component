##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Locale Component Architecuture interfaces

$Id: interfaces.py,v 1.1 2004/03/13 23:34:38 srichter Exp $
"""
from zope.interface import Interface
from zope.schema import Field
from zope.schema.interfaces import IEnumerated, IField, ITuple


class IInterfaceField(IEnumerated, IField):
    u"""A type of Field that has an Interfaces as its value."""

    basetype = Field(
        title=u"Base type",
        description=(u"All values must extend (or be) this type,"
                     u" unless it is None which means 'anything'."),
        default=Interface,
        )

class IInterfacesField(ITuple):
    u"""A type of Field that is has a tuple of Interfaces as its value."""

    basetype = Field(
            title=u"Base type",
            description=(u"All values must extend or be this type,"
                         u" unless it is None, which means 'anything'."),
            default=Interface,
            )
