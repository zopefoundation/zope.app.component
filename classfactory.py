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
"$Id: classfactory.py,v 1.6 2003/09/21 17:31:21 jim Exp $"

from zope.interface import implements, implementedBy
from zope.component.interfaces import IFactory
from zope.security.checker import NamesChecker, CheckerPublic

class ClassFactory:
    "Class that creates a factory component from a class"

    implements(IFactory)

    def __init__(self, _class, title='', description='', permission=None):
        self._class = _class
        self.title = title
        self.description = description
        if permission is not None:
            self.__Security_checker__ = NamesChecker(
                __call__ = permission,
                getInterfaces = CheckerPublic)

    def __call__(self, *args, **kwargs):
        return self._class(*args, **kwargs)

    def getInterfaces(self):
        return tuple(implementedBy(self._class))

__doc__ = "%s\n\n%s" % (ClassFactory.__doc__, __doc__)
