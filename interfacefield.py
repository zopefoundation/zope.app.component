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
$Id: interfacefield.py,v 1.6 2003/01/17 16:30:17 stevea Exp $
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

    # This is the most base basetype.
    # This isn't the default value. See the 'basetype' arg of __init__ for
    # that.
    basetype = None

    def __init__(self, basetype=Interface, *args, **kw):
        # XXX Workaround for None indicating a missing value
        if basetype is None:
            kw['required'] = False
        super(InterfaceField, self).__init__(*args, **kw)
        self.validate(basetype)
        self.basetype = basetype

    def _validate(self, value):
        super(InterfaceField, self)._validate(value)
        basetype = self.basetype

        if value is None and basetype is None:
            return

        if basetype is None:
            basetype = Interface

        if not IInterface.isImplementedBy(value):
            raise ValidationError("Not an interface", value)

        if not value.extends(basetype, 0):
            raise ValidationError("Does not extend", value, basetype)

class InterfacesField(Tuple):
    __doc__ = IInterfacesField.__doc__
    __implements__ = IInterfacesField

    # This is the most base basetype.
    # This isn't the default value. See the 'basetype' arg of __init__ for
    # that.
    basetype = None

    def __init__(self, basetype=Interface, default=(), *args, **kw):
        # XXX Workaround for None indicating a missing value
        if basetype is None:
            kw['required'] = False
        super(InterfacesField, self).__init__(default=default, *args, **kw)
        self.validate((basetype,))
        self.basetype = basetype
        # Not using schema.Sequence.value_types

    def _validate(self, value):
        super(InterfacesField, self)._validate(value)
        basetype = self.basetype
        if basetype is None:
            none_ok = True
            basetype = Interface
        else:
            none_ok = False
        for item in value:
            if item is None and none_ok:
                continue

            if not IInterface.isImplementedBy(item):
                raise ValidationError("Not an interface", item)

            if not item.extends(basetype, 0):
                raise ValidationError("Does not extend", item, basetype)

