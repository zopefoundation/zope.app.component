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
"""
$Id: globalinterfaceservice.py,v 1.13 2003/07/03 22:46:06 sidnei Exp $
"""
from __future__ import generators

__metaclass__ = type

from zope.component.exceptions import ComponentLookupError
from zope.app.interfaces.component import IGlobalInterfaceService
from zope.interface import implements

class InterfaceService:
    implements(IGlobalInterfaceService)

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.__data = data

    def getInterface(self, id):
        if id in self.__data:
            return self.__data[id][0]
        else:
            raise ComponentLookupError(id)

    def queryInterface(self, id, default=None):
        if self.__data.has_key(id):
            return self.__data[id][0]
        else:
            return default

    def searchInterface(self, search_string=None, base=None):
        return [t[1] for t in self.items(search_string, base)]

    def searchInterfaceIds(self, search_string=None, base=None):
        return [t[0] for t in self.items(search_string, base)]

    def items(self, search_string=None, base=None):
        if search_string:
            search_string = search_string.lower()

        for id, (interface, doc) in self.__data.items():
            if search_string:
                if doc.find(search_string) < 0:
                    continue
            if base is not None and not interface.extends(base, 0):
                continue
            yield id, interface

    def _getAllDocs(self,interface):
        docs = [str(interface.__name__).lower(),
                str(interface.__doc__).lower()]

        for name in interface:
            docs.append(str(interface.getDescriptionFor(name).__doc__).lower())

        return '\n'.join(docs)

    def provideInterface(self, id, interface):
        if not id:
            id = "%s.%s" % (interface.__module__, interface.__name__)

        self.__data[id]=(interface, self._getAllDocs(interface))

    _clear = __init__



interfaceService = InterfaceService()
provideInterface = interfaceService.provideInterface
getInterface = interfaceService.getInterface
queryInterface = interfaceService.queryInterface
searchInterface = interfaceService.searchInterface

_clear = interfaceService._clear

from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
