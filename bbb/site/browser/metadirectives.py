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
"""'tool' directive for 'browser' namespace

$Id$
"""
from zope.configuration.fields import GlobalInterface, PythonIdentifier, MessageID
from zope.interface import Interface

class IToolDirective(Interface):
    """Directive implementing basic tool support."""
    folder = PythonIdentifier(
        title=u"Destination Folder",
        description=u"""Destination Folder in which the tool instances are
                        placed.""",
        required=False,
        default=u"tools")
    
    title = MessageID(
        title=u"Title",
        description=u"""The title of the tool.""",
        required=False
        )

    description = MessageID(
        title=u"Description",
        description=u"Narrative description of what the tool represents.",
        required=False
        )
    
class IUtilityToolDirective(IToolDirective):
    """Directive for creating new utility-based tools."""

    interface = GlobalInterface(
        title=u"Interface",
        description=u"Interface used to filter out the available entries in a \
                      tool",
        required=True)
    
class IServiceToolDirective(IToolDirective):
    """Directive for specifying service-based tools."""
