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
"""Interface fields tests

$Id: test_interfacefield.py,v 1.4 2003/01/06 18:39:34 stevea Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.interface import Interface
import zope.interface as InterfaceModule
from zope.app.component.interfacefield import InterfaceField, InterfacesField
from zope.schema.interfaces import ValidationError

class TestInterfaceField(TestCase):

    def test_validate(self):
        field = InterfaceField()

        field.validate(Interface)
        class I(Interface): pass
        field.validate(I)

        self.assertRaises(ValidationError, field.validate, InterfaceModule)
        class I: pass
        self.assertRaises(ValidationError, field.validate, I)

    def test_validate_w_type(self):

        class I1(Interface): pass
        class I2(I1): pass
        class I3(I2): pass

        field = InterfaceField(basetype=I2)

        field.validate(I2)
        field.validate(I3)

        self.assertRaises(ValidationError, field.validate, Interface)
        self.assertRaises(ValidationError, field.validate, I1)
        self.assertRaises(ValidationError, field.validate, None)

    def test_validate_w_none(self):
        class I1(Interface): pass

        field = InterfaceField(basetype=None)

        field.validate(None)
        field.validate(Interface)
        field.validate(I1)

class TestInterfacesField(TestCase):

    def test_validate(self):
        field = InterfacesField()
        field.validate(())
        field.validate((Interface,))
        class I(Interface): pass
        field.validate((I,))

        self.assertRaises(ValidationError, field.validate, (InterfaceModule,))
        class I: pass
        self.assertRaises(ValidationError, field.validate, (I,))

    def test_validate_w_type(self):

        class I1(Interface): pass
        class I2(I1): pass
        class I3(I2): pass

        field = InterfacesField(basetype=I2)

        field.validate((I2,))
        field.validate((I3,))

        self.assertRaises(ValidationError, field.validate, (Interface,))
        self.assertRaises(ValidationError, field.validate, (I1,))
        self.assertRaises(ValidationError, field.validate, (None,))

    def test_validate_w_none(self):
        class I1(Interface): pass

        field = InterfacesField(basetype=None)

        field.validate((None,))
        field.validate((Interface,))
        field.validate((I1,))

def test_suite():
    return TestSuite((makeSuite(TestInterfaceField),
                      makeSuite(TestInterfacesField),
                    ))

if __name__=='__main__':
    main(defaultTest='test_suite')
