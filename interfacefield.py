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
"""These are the interfaces for the common fields.

$Id: interfacefield.py,v 1.2 2002/12/25 14:12:45 jim Exp $
"""

from zope.schema import ValueSet
from zope.interface import Interface
from zope.interface.interfaces import IInterface
from zope.schema.interfaces import ValidationError
from zope.app.interfaces.component.interfacefield import IInterfaceField

class InterfaceField(ValueSet):
    __doc__ = IInterfaceField.__doc__
    __implements__ = IInterfaceField

    type = Interface

    def __init__(self, type=Interface, *args, **kw):
        super(InterfaceField, self).__init__(*args, **kw)
        self.validate(type)
        self.type = type

    def _validate(self, value):
        super(InterfaceField, self)._validate(value)

        if not IInterface.isImplementedBy(value):
            raise ValidationError("Not an interface", value)

        if not value.extends(self.type, 0):
            raise ValidationError("Does not extend", value, self.type)
