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
import zope.component
import zope.app.component.interfaces
from zope.app import zapi

# BBB: Will go away in 3.3.
from zope.app.component.bbb import localservice
import sys
sys.modules['zope.app.component.localservice'] = localservice

_marker = object()

def getNextSiteManager(context):
    """Get the next site manager."""
    sm = queryNextSiteManager(context, _marker)
    if sm is _marker:
        raise zope.component.interfaces.ComponentLookupError(
              "No more site managers have been found.")
    return sm


def queryNextSiteManager(context, default=None):
    """Get the next site manager.

    If the site manager of the given context is the global site manager, then
    `default` is returned.
    """
    sm = zapi.getSiteManager(context)
    if not zope.app.component.interfaces.ILocalSiteManager.providedBy(sm):
        return default

    bases = sm.__bases__
    if not bases:
        return zapi.getGlobalSiteManager()
    return bases[0]


def getNextUtility(context, interface, name=''):
    """Get the next available utility.

    If no utility was found, a `ComponentLookupError` is raised.
    """
    util = queryNextUtility(context, interface, name, _marker)
    if util is _marker:
        raise zope.component.interfaces.ComponentLookupError(
              "No more utilities for %s, '%s' have been found." % (
                  interface, name))
    return util


def queryNextUtility(context, interface, name='', default=None):
    """Query for the next available utility.

    Find the next available utility providing `interface` and having the
    specified name. If no utility was found, return the specified `default`
    value."""    
    sm = queryNextSiteManager(context)
    if sm is None:
        return default
    return sm.queryUtility(interface, name, default)
