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
"""Tests for the registered view support.

$Id$
"""
import unittest

from zope.app.tests import ztapi
from zope.app.utility.browser import Utilities
from zope.app.tests import placelesssetup
from zope.interface import Interface, implements
from zope.publisher.browser import TestRequest
from zope.app.publisher.browser import BrowserView


class IFoo(Interface):
    """Sample interface."""
    def someMethod(someArg):
        """Sample interface method."""

class IBar(IFoo):
    """Derived interface."""
    def anotherMethod():
        """Another example method interface."""

class IStub(Interface):
    """Interface used to bind an absolute_url view to stub objects."""

class Stub(object):
    # Does triple duty as a stub for a registration, ay registration
    # stack, and a component!

    implements(IStub)

    def __init__(self, name, provided, url=None):
        self.url = url
        self.name = name
        self.provided = provided
        self.component = self

    # registration registry
    def active(self):
        if self.url:
            return self
        else:
            return None

    def info(self):
        return [{'registration': self}]

    # registration
    def getComponent(self):
        return self.component

    def usageSummary(self):
        return ""

class StubAbsoluteURL(BrowserView):
    def __str__(self):
        return self.context.url

class StubLocalUtilityService(object):
    def registrations(self, localOnly=False):
        return iter([
            Stub('', IFoo, "1"),
            Stub('myfoo-1', IFoo, "2"),
            Stub('myfoo-2', IFoo),
            Stub('', IBar),
            Stub('mybar-1', IBar, "3")
            ])

    def queryRegistrationsFor(self, registration):
        return registration

class UtilitiesView(Utilities, BrowserView):
    """Adding BrowserView to Utilities; this is usually done by ZCML."""


class RegisteredTest(placelesssetup.PlacelessSetup, unittest.TestCase):

    def test_utility(self):
        ztapi.browserView(IStub,
                          "absolute_url",
                          StubAbsoluteURL)
        utilityservice = StubLocalUtilityService()
        request = TestRequest()
        utilities = UtilitiesView(utilityservice, request)
        ifname1 = __name__ + ".IFoo"
        ifname2 = __name__ + ".IBar"
        def confurl(ifname, name):
            return ("@@configureutility.html?interface=%s&name=%s"
                    % (ifname, name))
        expected = [{"interface": ifname2,
                     "name": "",
                     "url": "",
                     "summary": "",
                     "configurl": confurl(ifname2, '')},
                    {"interface": ifname2,
                     "name": "mybar-1",
                     "url": "3",
                     "summary": "",
                     "configurl": confurl(ifname2, 'mybar-1')},
                    {"interface": ifname1,
                     "name": "",
                     "url": "1",
                     "summary": "",
                     "configurl": confurl(ifname1, '')},
                    {"interface": ifname1,
                     "name": "myfoo-1",
                     "url": "2",
                     "summary": "",
                     "configurl": confurl(ifname1, 'myfoo-1')},
                    {"interface": ifname1,
                     "name": "myfoo-2",
                     "url": "",
                     "summary": "",
                     "configurl": confurl(ifname1, 'myfoo-2')},
                    ]
        result = utilities.getConfigs()
        self.assertEqual(len(expected), len(result))
        for r, e in zip(result, expected):
            ri = r.items()
            ri.sort()
            ei = e.items()
            ei.sort()
            self.assertEqual(ri, ei)


def test_suite():
    return unittest.makeSuite(RegisteredTest)
