##############################################################################
#
# Copyright (c) 2001-2007 Zope Foundation and Contributors.
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
"Non-API test details."


from zope.browsermenu.menu import getFirstMenuItem
from zope.interface import implementer
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserPublisher


@implementer(IBrowserPublisher)
class ManagementViewSelector(BrowserView):
    """View that selects the first available management view.

    Support 'zmi_views' actions like: 'javascript:alert("hello")',
    '../view_on_parent.html' or '++rollover++'.
    """
    # Copied from zope.app.publication
    # Simplified to assert just the test case we expect.

    def browserDefault(self, request):
        return self, ()

    def __call__(self):
        item = getFirstMenuItem('zmi_views', self.context, self.request)
        assert item
        redirect_url = item['action']
        if not redirect_url.lower().startswith(('../', 'javascript:', '++')):
            self.request.response.redirect(redirect_url)
            return ''
        raise AssertionError("Should not get here")  # pragma: no cover


class LoginLogout:
    # Dummy implementation of zope.app.security.browser.auth.LoginLogout

    def __call__(self):
        return None
