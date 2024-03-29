##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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
"""View support for adding and configuring utilities and adapters.
"""
import zope.component
import zope.component.interfaces
from zope.app.container.browser.adding import Adding
from zope.component.interfaces import IFactory
from zope.exceptions.interfaces import UserError
from zope.publisher.browser import BrowserView
from zope.security.proxy import removeSecurityProxy
from zope.site.site import LocalSiteManager
from zope.traversing.browser.absoluteurl import absoluteURL

from zope.app.component.i18n import ZopeMessageFactory as _


class ComponentAdding(Adding):
    """Adding subclass used for registerable components."""

    menu_id = "add_component"

    def add(self, content):
        # Override so as to save a reference to the added object
        self.added_object = super().add(content)
        return self.added_object

    def nextURL(self):
        v = zope.component.queryMultiAdapter(
            (self.added_object, self.request), name="registration.html")
        if v is not None:
            url = str(zope.component.getMultiAdapter(
                (self.added_object, self.request), name='absolute_url'))
            return url + "/@@registration.html"

        return super().nextURL()  # pragma: no cover

    def action(self, type_name, id=''):
        # For special case of that we want to redirect to another adding view
        # (usually another menu such as AddUtility)
        if type_name.startswith("../"):  # pragma: no cover
            # Special case
            url = type_name
            if id:
                url += "?id=" + id
            self.request.response.redirect(url)
            return

        # Call the superclass action() method.
        # As a side effect, self.added_object is set by add() above.
        super().action(type_name, id)

    _addFilterInterface = None

    def addingInfo(self):
        # A site management folder can have many things. We only want
        # things that implement a particular interface
        info = super().addingInfo()
        if self._addFilterInterface is None:
            return info
        out = []
        for item in info:
            extra = item.get('extra')
            if extra:
                factoryname = extra.get('factory')
                if factoryname:
                    factory = zope.component.getUtility(IFactory, factoryname)
                    intf = factory.getInterfaces()
                    if not intf.extends(self._addFilterInterface):
                        # We only skip new addMenuItem style objects
                        # that don't implement our wanted interface.
                        continue

            out.append(item)

        return out


class UtilityAdding(ComponentAdding):
    """Adding subclass used for adding utilities."""

    menu_id = None
    title = _("Add Utility")

    def nextURL(self):
        v = zope.component.queryMultiAdapter(
            (self.added_object, self.request), name="addRegistration.html")
        if v is not None:
            url = absoluteURL(self.added_object, self.request)
            return url + "/@@addRegistration.html"

        return super().nextURL()  # pragma: no cover


class MakeSite(BrowserView):
    """View for converting a possible site to a site."""

    def addSiteManager(self):
        """Convert a possible site to a site

        >>> from zope.traversing.interfaces import IContainmentRoot
        >>> from zope.interface import implementer

        >>> @implementer(IContainmentRoot)
        ... class PossibleSite(object):
        ...     def setSiteManager(self, sm):
        ...         from zope.interface import directlyProvides
        ...         directlyProvides(self, zope.component.interfaces.ISite)


        >>> folder = PossibleSite()

        >>> from zope.publisher.browser import TestRequest
        >>> request = TestRequest()

        Now we'll make our folder a site:

        >>> MakeSite(folder, request).addSiteManager()

        Now verify that we have a site:

        >>> zope.component.interfaces.ISite.providedBy(folder)
        1

        Note that we've also redirected the request:

        >>> request.response.getStatus()
        302

        >>> request.response.getHeader('location')
        '++etc++site/@@SelectedManagementView.html'

        If we try to do it again, we'll fail:

        >>> MakeSite(folder, request).addSiteManager()
        Traceback (most recent call last):
        ...
        zope.exceptions.interfaces.UserError: This is already a site

        """
        if zope.component.interfaces.ISite.providedBy(self.context):
            raise UserError(_('This is already a site'))

        # We don't want to store security proxies (we can't,
        # actually), so we have to remove proxies here before passing
        # the context to the SiteManager.
        bare = removeSecurityProxy(self.context)
        sm = LocalSiteManager(bare)
        self.context.setSiteManager(sm)
        self.request.response.redirect(
            "++etc++site/@@SelectedManagementView.html")
