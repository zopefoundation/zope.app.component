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
$Id: globalinterfaceservice.py,v 1.18 2003/11/05 03:08:21 jeremy Exp $
"""
__metaclass__ = type

from zope.component.exceptions import ComponentLookupError
from zope.component import getService
from zope.app.interfaces.component import IGlobalInterfaceService
from zope.interface import implements, providedBy
from zope.interface.interfaces import IInterface
from zope.component.utility import utilityService

class InterfaceService:
    implements(IGlobalInterfaceService)

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.__data = data

    def getInterface(self, id):
        iface = self.queryInterface(id, None)
        if iface is None:
            raise ComponentLookupError(id)
        return iface

    def queryInterface(self, id, default=None):
        if self.__data.has_key(id):
            return self.__data[id][0]
        else:
            # XXX Should use getService(), but that breaks a few
            # tests that do too basic setup to get the utilities
            # service started. I'll fix this later
            utilities = self._queryUtilityInterfaces(search_string=id)
            if utilities:
                return utilities[0][1]
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

        for id, interface in self._queryUtilityInterfaces(base, search_string):
            yield id, interface

    def _getAllDocs(self,interface):
        docs = [str(interface.getName()).lower(),
                str(interface.__doc__).lower()]

        for name in interface:
            docs.append(str(interface.getDescriptionFor(name).__doc__).lower())

        return '\n'.join(docs)

    def _queryUtilityInterfaces(self, interface=None, search_string=None):
        # XXX Should use getService(), but that breaks a few
        # tests that do too basic setup to get the utilities
        # service started. I'll fix this later
        matching = utilityService.getUtilitiesFor(interface)
        matching = [m for m in matching
                    if IInterface in providedBy(m[1])]
        if search_string is not None:
            return [match for match in matching
                    if match[0].find(search_string) > -1]
        return matching

    def provideInterface(self, id, interface):
        if not id:
            id = "%s.%s" % (interface.__module__, interface.getName())

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
