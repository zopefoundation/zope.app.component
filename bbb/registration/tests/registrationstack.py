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
"""Registration Stack

$Id$
"""
from zope.app.registration.registration import RegistrationStatusProperty
from zope.app.container.contained import Contained
from zope.app.traversing.interfaces import IPhysicallyLocatable
import zope.interface

class TestingRegistration(Contained):
    zope.interface.implements(IPhysicallyLocatable)

    status = RegistrationStatusProperty()

    def __init__(self, id):
        self.id = str(id)

    def __eq__(self, other):
        return self.id == getattr(other, 'id', 0)

    def getPath(self):
        return self.id

    def __repr__(self):
        return self.id

    
from zope.app.registration.registration import RegistrationStack

def TestingRegistrationStack(*regs):
    regs = list(regs)
    regs.reverse()
    stack = RegistrationStack(None)
    for reg in regs:
        stack.register(reg)
        stack.activate(reg)
    return stack
