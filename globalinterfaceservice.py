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
$Id: globalinterfaceservice.py,v 1.4 2003/01/03 16:03:33 stevea Exp $
"""

from zope.interface import Interface
from zope.component.exceptions import ComponentLookupError

class IInterfaceService(Interface):
    """Service that keeps track of used interfaces
    """

    def getInterface(id):
        """Return the interface registered for the given id

        A ComponentLookupError is raised if the interface can't be found.
        """

    def queryInterface(id, default=None):
        """Return the interface registered for the given id

        The default is returned if the interface can't be found.
        """

    def searchInterface(search_string='', base=None):
        """Return the interfaces that match the search criteria

        If a search string is given, only interfaces that contain the
        string in their documentation will be returned.

        If base is given, only interfaces that equal or extend base
        will be returned.

        """

    def searchInterfaceIds(search_string='', base=None):
        """Return the ids of the interfaces that match the search criteria.

        See searchInterface

        """

from zope.app.interfaces.component.globalinterfaceservice \
        import IGlobalInterfaceService

class InterfaceService:
    __implements__ = IGlobalInterfaceService

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.__data = data

    def getInterface(self, id):
        if id in self.__data:
            return self.__data[id][0]
        else:
            raise ComponentLookupError

    def queryInterface(self, id, default=None):
        if self.__data.has_key(id):
            return self.__data[id][0]
        else:
            return default

    def searchInterfaceIds(self, search_string='', base=None):
        result = []

        data = self.__data
        search_string = search_string.lower()

        for id in data:
            interface, doc = data[id]

            if search_string:
                if doc.find(search_string) < 0:
                    continue

            if base is not None and not interface.extends(base, 0):
                continue

            result.append(id)

        return result

    def searchInterface(self, search_string='', base=None):
        data = self.__data
        return [data[id][0]
                for id in self.searchInterfaceIds(search_string, base)]

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
