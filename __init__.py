##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Local Component Architecture

$Id$
"""
__docformat__ = "reStructuredText"


_marker = object()

def getNextUtility(context, interface, name=''):
    """Get the next available utility.

    If no utility was found, a `ComponentLookupError` is raised.
    """
    util = queryNextUtility(context, interface, name, _marker)
    if util is _marker:
        raise ComponentLookupError, \
              "No more utilities for %s, '%s' have been found." %(interface,
                                                                  name)
    return util


def queryNextUtility(context, interface, name='', default=None):
    """Query for the next available utility.

    Find the next available utility providing `interface` and having the
    specified name. If no utility was found, return the specified `default`
    value.

    It is very important that this method really finds the next utility and
    does not abort, if the utility was not found in the next utility service.

    Let's start out by declaring a utility interface and an implementation:

      >>> from zope.interface import Interface, implements
      >>> class IAnyUtility(Interface):
      ...     pass
      
      >>> class AnyUtility(object):
      ...     implements(IAnyUtility)
      ...     def __init__(self, id):
      ...         self.id = id
      
      >>> any1 = AnyUtility(1)
      >>> any1next = AnyUtility(2)

    Now that we have the utilities, let's register them:

      >>> testingNextUtility(any1, any1next, IAnyUtility)

    The next utility of `any1` ahould be `any1next`:

      >>> queryNextUtility(any1, IAnyUtility) is any1next
      True

    But `any1next` does not have a next utility, so the default is returned:

      >>> queryNextUtility(any1next, IAnyUtility) is None
      True

    """    
    util = _marker
    while util is _marker:
        utilservice = queryNextService(context, zapi.servicenames.Utilities)
        if utilservice is None:
            return default
        util = utilservice.queryUtility(interface, name, _marker)
        context = utilservice
        
    return util
