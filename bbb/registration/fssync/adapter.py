##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""File-system synchronization for registrations.

$Id$
"""
from zope.interface import implements

from zope.fssync.server.entryadapter import ObjectEntryAdapter
from zope.fssync.server.interfaces import IObjectFile
from zope.proxy import removeAllProxies
from zope.xmlpickle import dumps, loads


class ComponentRegistrationAdapter(ObjectEntryAdapter):
    """Fssync adapter for ComponentRegistration objects and subclasses.

    This is fairly generic -- it should apply to most subclasses of
    ComponentRegistration.  But in order for it to work for a
    specific subclass (say, UtilityRegistration), you have to (a) add
    an entry to configure.zcml, like this:

        <fssync:adapter
            class=".utility.UtilityRegistration"
            factory=".registration.fssync.ComponentRegistrationAdapter"
            />

    and (b) add a function to factories.py, like this:

        def UtilityRegistration():
            from zope.app.utility import UtilityRegistration
            return UtilityRegistration("", None, None)

    The file representation of a registration object is an XML pickle
    for a modified version of the instance dict.  In this version of
    the instance dict, the __annotations__ attribute is omitted,
    because annotations are already stored on the filesystem in a
    different way (in @@Zope/Annotations/<file>).
    """

    implements(IObjectFile)

    def factory(self):
        """See IObjectEntry."""
        name = self.context.__class__.__name__
        return "zope.app.registration.factories." + name

    def getBody(self):
        """See IObjectEntry."""
        obj = removeAllProxies(self.context)
        ivars = {}
        ivars.update(obj.__getstate__())
        aname = "__annotations__"
        if aname in ivars:
            del ivars[aname]
        return dumps(ivars)

    def setBody(self, body):
        """See IObjectEntry."""
        obj = removeAllProxies(self.context)
        ivars = loads(body)
        obj.__setstate__(ivars)
