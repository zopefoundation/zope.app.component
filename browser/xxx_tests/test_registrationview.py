##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Tests for the RegistrationView view class.

$Id$
"""
from zope.interface import implements
from zope.publisher.browser import TestRequest
from zope.testing.doctestunit import DocTestSuite

from zope.app.registration.interfaces import IRegistered
from zope.app.registration.interfaces import RegisteredStatus
from zope.app.registration.interfaces import ActiveStatus

from zope.app.registration.browser import RegistrationView


def test():
    """
    >>> request = TestRequest()

    Check results when using an unregisted object:

    >>> view = RegistrationView(FakeRegisterable([]), request)
    >>> view.registered()
    0

    Returns for the active() and registration() methods are undefined
    for unregistred objects.

    The update() method shouldn't do anything with an action specified
    in the form:

    >>> request.response.setStatus(200)
    >>> view.update()
    >>> view.registered()
    0
    >>> request.response.getStatus()
    200

    This simulates submitting the form using the 'Activate' button:

    >>> request.form['activate'] = 'Activate'
    >>> view.update()
    >>> request.response.getStatus()
    302
    >>> request.response.getHeader('location')
    'addRegistration.html'

    Let's look at the case when the object has a single registration
    to begin with:

    >>> request = TestRequest()
    >>> reg = FakeRegistration(RegisteredStatus)
    >>> view = RegistrationView(FakeRegisterable([reg]), request)
    >>> view.active()
    0
    >>> view.registered()
    1
    >>> view.registration() is reg
    1

    Make sure calling update() without an action doesn't change the
    registration:

    >>> request.response.setStatus(200)
    >>> view.update()
    >>> request.response.getStatus()
    200
    >>> view.active()
    0
    >>> view.registered()
    1
    >>> view.registration() is reg
    1

    Now test activating the object:

    >>> request.form['activate'] = 'Activate'
    >>> request.response.setStatus(200)
    >>> view.update()
    >>> request.response.getStatus()
    200
    >>> view.active()
    1
    >>> view.registered()
    1
    >>> view.registration() is reg
    1
    >>> reg.status == ActiveStatus
    1

    Now test deactivating an active object:

    >>> request.form = {'deactivate': 'Deactivate'}
    >>> request.response.setStatus(200)
    >>> view.update()
    >>> request.response.getStatus()
    200
    >>> view.active()
    0
    >>> view.registered()
    1
    >>> view.registration() is reg
    1
    >>> reg.status == RegisteredStatus
    1
    """

def test_multiple_registrations():
    """
    >>> request = TestRequest()
    >>> reg1 = FakeRegistration(RegisteredStatus)
    >>> reg2 = FakeRegistration(ActiveStatus)
    >>> view = RegistrationView(FakeRegisterable([reg1, reg2]), request)
    >>> view.active()
    0
    >>> view.registered()
    1
    >>> view.registration() is reg1
    1

    Now make sure this view redirects us to the advanced registrations
    form since we have more than one registraion:

    >>> request.response.setStatus(200)
    >>> view.update()
    >>> request.response.getStatus()
    302
    """


class FakeRegisterable(object):
    implements(IRegistered)

    def __init__(self, usages):
        self._usages = usages

    def registrations(self):
        return self._usages

class FakeRegistration(object):

    def __init__(self, status):
        self.status = status


def test_suite():
    return DocTestSuite()
