##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Interface utility functions

$Id$
"""
from zope.component.exceptions import ComponentLookupError
from zope.interface import directlyProvides
from zope.interface.interfaces import IInterface
from types import ClassType
from zope.app import zapi

def provideInterface(id, interface, iface_type=None):
    """register Interface with utility service

    >>> from zope.app.tests.placelesssetup import setUp, tearDown
    >>> setUp()
    >>> utilities = zapi.getGlobalService(zapi.servicenames.Utilities)
    >>> from zope.interface import Interface
    >>> from zope.interface.interfaces import IInterface
    >>> from zope.app.content.interfaces import IContentType
    >>> class I(Interface):
    ...     pass
    >>> IInterface.providedBy(I)
    True
    >>> IContentType.providedBy(I)
    False
    >>> interfaces = utilities.getUtilitiesFor(IContentType)
    >>> list(interfaces)
    []
    >>> provideInterface('', I, IContentType)
    >>> IContentType.providedBy(I)
    True
    >>> interfaces = list(utilities.getUtilitiesFor(IContentType))
    >>> [name for (name, iface) in interfaces]
    [u'zope.app.component.interface.I']
    >>> [iface.__name__ for (name, iface) in interfaces]
    ['I']
    >>> class I1(Interface):
    ...     pass
    >>> provideInterface('', I1)
    >>> IInterface.providedBy(I1)
    True
    >>> IContentType.providedBy(I1)
    False
    >>> interfaces = list(utilities.getUtilitiesFor(IContentType))
    >>> [name for (name, iface) in interfaces]
    [u'zope.app.component.interface.I']
    >>> [iface.__name__ for (name, iface) in interfaces]
    ['I']
    >>> tearDown()
    
    """
    if not id:
        id = "%s.%s" % (interface.__module__, interface.__name__)

    if not IInterface.providedBy(interface):
        if not isinstance(interface, (type, ClassType)):
            raise TypeError(id, "is not an interface or class")
        return

    if iface_type is not None:
        if not iface_type.extends(IInterface):
            raise TypeError(iface_type, "is not an interface type")
        directlyProvides(interface, iface_type)
    else:
        iface_type = IInterface
        
    utilityService = zapi.getGlobalService(zapi.servicenames.Utilities)
    utilityService.provideUtility(iface_type, interface, name=id)



def getInterface(context, id):
    """return interface or ComponentLookupError

    >>> from zope.app.tests.placelesssetup import setUp, tearDown
    >>> setUp()
    >>> utilities = zapi.getGlobalService(zapi.servicenames.Utilities)
    >>> from zope.interface import Interface
    >>> from zope.app.content.interfaces import IContentType
    >>> class I4(Interface):
    ...     pass
    >>> IInterface.providedBy(I4)
    True
    >>> IContentType.providedBy(I4)
    False
    >>> getInterface(None, 'zope.app.component.interface.I4')
    Traceback (most recent call last):
    ...
    ComponentLookupError: 'zope.app.component.interface.I4'
    >>> provideInterface('', I4, IContentType)
    >>> IContentType.providedBy(I4)
    True
    >>> iface = queryInterface( """\
                """ 'zope.app.component.interface.I4')
    >>> iface.__name__
    'I4'
    >>> tearDown()
    
    """
    iface = queryInterface(id, None)
    if iface is None:
        raise ComponentLookupError(id)
    return iface

def queryInterface(id, default=None):
    """return interface or None

    >>> from zope.app.tests.placelesssetup import setUp, tearDown
    >>> tearDown()
    >>> setUp()
    >>> utilities = zapi.getGlobalService(zapi.servicenames.Utilities)
    >>> from zope.interface import Interface
    >>> from zope.interface.interfaces import IInterface
    >>> from zope.app.content.interfaces import IContentType
    >>> class I3(Interface):
    ...     pass
    >>> IInterface.providedBy(I3)
    True
    >>> IContentType.providedBy(I3)
    False
    >>> queryInterface('zope.app.component.interface.I3')
    
    >>> provideInterface('', I3, IContentType)
    >>> IContentType.providedBy(I3)
    True
    >>> iface = queryInterface('zope.app.component.interface.I3')
    >>> iface.__name__
    'I3'
    >>> tearDown()
    
    """
    
    return zapi.queryUtility(IInterface, id, default)

def searchInterface(context, search_string=None, base=None):
    """Interfaces search

    >>> from zope.app.tests.placelesssetup import setUp, tearDown
    >>> setUp()
    >>> utilities = zapi.getGlobalService(zapi.servicenames.Utilities)
    >>> from zope.interface import Interface
    >>> from zope.interface.interfaces import IInterface
    >>> from zope.app.content.interfaces import IContentType
    >>> class I5(Interface):
    ...     pass
    >>> IInterface.providedBy(I5)
    True
    >>> IContentType.providedBy(I5)
    False
    >>> searchInterface(None, 'zope.app.component.interface.I5')
    []
    >>> provideInterface('', I5, IContentType)
    >>> IContentType.providedBy(I5)
    True
    >>> iface = searchInterface(None,
    ...                        'zope.app.component.interface.I5')
    >>> iface[0].__name__
    'I5'
    >>> tearDown()

    """

    return [iface_util[1]
            for iface_util in
            searchInterfaceUtilities(context, search_string, base)]


def searchInterfaceIds(context, search_string=None, base=None):
    """Interfaces search

    >>> from zope.app.tests.placelesssetup import setUp, tearDown
    >>> setUp()
    >>> utilities = zapi.getGlobalService(zapi.servicenames.Utilities)
    >>> from zope.interface import Interface
    >>> from zope.interface.interfaces import IInterface
    >>> from zope.app.content.interfaces import IContentType
    >>> class I5(Interface):
    ...     pass
    >>> IInterface.providedBy(I5)
    True
    >>> IContentType.providedBy(I5)
    False
    >>> searchInterface(None, 'zope.app.component.interface.I5')
    []
    >>> provideInterface('', I5, IContentType)
    >>> IContentType.providedBy(I5)
    True
    >>> iface = searchInterfaceIds(None,
    ...                        'zope.app.component.interface.I5')
    >>> iface
    [u'zope.app.component.interface.I5']
    >>> tearDown()

    """

    return [iface_util[0]
            for iface_util in
            searchInterfaceUtilities(context, search_string, base)]


def searchInterfaceUtilities(context, search_string=None, base=None):
    utilityService = zapi.getGlobalService(zapi.servicenames.Utilities)   
    iface_utilities = utilityService.getUtilitiesFor(IInterface)

    if search_string:
        search_string = search_string.lower()
        iface_utilities = [iface_util for iface_util in iface_utilities
                           if (getInterfaceAllDocs(iface_util[1]).\
                               find(search_string) >= 0)]
    if base:
        res = [iface_util for iface_util in iface_utilities
               if iface_util[1].extends(base)]
    else:
        res = [iface_util for iface_util in iface_utilities]
    return res


def getInterfaceAllDocs(interface):
    iface_id = '%s.%s' %(interface.__module__, interface.__name__)
    docs = [str(iface_id).lower(),
            str(interface.__doc__).lower()]

    if IInterface.providedBy(interface):
        for name in interface:
            docs.append(
                str(interface.getDescriptionFor(name).__doc__).lower())

    return '\n'.join(docs)


def nameToInterface(context, id):
    if id == 'None':
        return None
    iface = getInterface(context, id)
    return iface

