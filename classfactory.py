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
"$Id: classfactory.py,v 1.2 2002/12/25 14:12:45 jim Exp $"

from zope.component.interfaces import IFactory

class ClassFactory:
    "Class that creates a factory component from a class"

    __implements__ = IFactory

    def __init__(self, _class):
        self._class = _class

    def __call__(self, *args, **kwargs):
        return self._class(*args, **kwargs)

    def getInterfaces(self):
        return getattr(self._class, '__implements__', None)

__doc__ = "%s\n\n%s" % (ClassFactory.__doc__, __doc__)
