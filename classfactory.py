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
"$Id: classfactory.py,v 1.5 2003/08/04 23:12:44 sidnei Exp $"

from zope.interface import implements, implementedBy
from zope.component.interfaces import IFactory

class ClassFactory:
    "Class that creates a factory component from a class"

    implements(IFactory)

    def __init__(self, _class, title='', description=''):
        self._class = _class
        self.title = title
        self.description = description

    def __call__(self, *args, **kwargs):
        return self._class(*args, **kwargs)

    def getInterfaces(self):
        return tuple(implementedBy(self._class))

__doc__ = "%s\n\n%s" % (ClassFactory.__doc__, __doc__)
