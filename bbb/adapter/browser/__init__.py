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
"""Views for local adapter registration.

  AdapterSeviceView -- it's a bit different from other services, as it
  has a lot of things in it, so we provide a search interface:

    search page
    browsing page

  `AdapterRegistrationAdd`

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.app.form.utility import setUpWidgets, getWidgetsData

from zope.schema import getFieldNamesInOrder
from zope.app.publisher.browser import BrowserView

from zope.app.adapter.adapter import IAdapterRegistration
from zope.app.registration.interfaces import IRegistration
from zope.app.form.interfaces import IInputWidget
from zope.app.form.utility import applyWidgetsChanges
from zope.event import notify
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.adapter.adapter import AdapterRegistration

class AdapterRegistrationAdd(BrowserView):

    def __init__(self, *args):
        super(AdapterRegistrationAdd, self).__init__(*args)
        setUpWidgets(self, IAdapterRegistration, IInputWidget)

    def refresh(self):
        if "FINISH" in self.request:
            data = getWidgetsData(self, IAdapterRegistration)
            registration = AdapterRegistration(**data)
            notify(ObjectCreatedEvent(registration))
            registration = self.context.add(registration)
            applyWidgetsChanges(view, IRegistration, target=registration) 
            self.request.response.redirect(self.context.nextURL())
            return False

        return True

    def getWidgets(self):
        return ([getattr(self, name)
                 for name in getFieldNamesInOrder(IAdapterRegistration)]
                +
                [getattr(self, name)
                 for name in getFieldNamesInOrder(IRegistration)]
                )
