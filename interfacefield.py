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
"""
$Id: interfacefield.py,v 1.4 2003/01/05 18:56:47 stevea Exp $
"""

from zope.schema import ValueSet, Tuple
from zope.interface import Interface
from zope.interface.interfaces import IInterface
from zope.schema.interfaces import ValidationError
from zope.app.interfaces.component.interfacefield import IInterfaceField
from zope.app.interfaces.component.interfacefield import IInterfacesField

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

class InterfacesField(Tuple):
    __doc__ = IInterfacesField.__doc__
    __implements__ = IInterfacesField

    value_type = Interface

    def __init__(self, value_type=Interface, default=(), *args, **kw):
        super(InterfacesField, self).__init__(default=default, *args, **kw)
        self.validate((value_type,))
        self.value_type = value_type
        # Not using schema.Sequence.value_types

    def _validate(self, value):
        super(InterfacesField, self)._validate(value)
        for item in value:
            if not IInterface.isImplementedBy(item):
                raise ValidationError("Not an interface", item)

            if not item.extends(self.value_type, 0):
                raise ValidationError("Does not extend", item, self.value_type)
