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
"""Unit tests for registration classes

$Id$
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.testing.doctestunit import DocTestSuite

import zope.interface
from zope.interface import Interface, implements
from zope.security.proxy import Proxy

from zope.app.annotation.interfaces import IAnnotations
from zope.app.container.contained import Contained
from zope.app.container.contained import ObjectRemovedEvent, ObjectMovedEvent
from zope.app.container.interfaces import IObjectRemovedEvent
from zope.app.dependable.interfaces import IDependable
from zope.app.registration.interfaces import IRegistration
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.tests import ztapi, placelesssetup
from zope.app.traversing.api import traverse
from zope.app.traversing.interfaces import IPhysicallyLocatable

from zope.app.registration.interfaces import UnregisteredStatus
from zope.app.registration.interfaces import RegisteredStatus
from zope.app.registration.interfaces import ActiveStatus
from zope.app.registration.interfaces import IRegisterable
from zope.app.registration.interfaces import IRegistered
from zope.app.dependable.interfaces import DependencyError
from zope.app.registration.registration import \
     SimpleRegistration, ComponentRegistration
from zope.app.registration.registration import \
    SimpleRegistrationRemoveSubscriber, \
    ComponentRegistrationRemoveSubscriber, \
    ComponentRegistrationAddSubscriber, \
    RegisterableMoveSubscriber
from zope.app.registration.registration import Registered
from zope.app.registration.registration import RegisterableCopier


class ITestComponent(Interface):
    pass

class ComponentStub(Contained):

    implements(IDependable)

    _dependents = ()

    def addDependent(self, location):
        self._dependents = tuple(
            [d for d in self._dependents if d != location]
            +
            [location]
            )

    def removeDependent(self, location):
        self._dependents = tuple(
            [d for d in self._dependents if d != location]
            )

    def dependents(self):
        return self._dependents


class DummyRegistration(ComponentStub):
    implements (IRegistration, IPhysicallyLocatable)

    def __init__(self):
        self.status = UnregisteredStatus
        self.component = self

    def getPath(self):
        return 'dummy!'

    def getComponent(self):
        return self


class DummyRegisterable(Contained, dict):

    implements(IRegisterable, IAnnotations)


class TestSimpleRegistrationEvents(TestCase):

    def test_RemoveSubscriber(self):
        reg = DummyRegistration()
        reg.status = ActiveStatus

        # we need to simulate an enclosing site manager:
        from zope.app.container.contained import Contained
        services = Contained()
        from zope.app.site.interfaces import ISiteManager
        zope.interface.directlyProvides(services, ISiteManager)
        reg.__parent__ = services

        # we need an event. Initially, we create an event simulating delete
        # of the services.  In this case, nothing should change:
        from zope.app.container.contained import ObjectRemovedEvent
        event = ObjectRemovedEvent(services)
        SimpleRegistrationRemoveSubscriber(reg, event)
        self.assertEquals(reg.status, ActiveStatus)

        # Now we'll "remove" the registration:
        event = ObjectRemovedEvent(reg)

        # test that removal fails with Active status
        self.assertRaises(DependencyError,
                          SimpleRegistrationRemoveSubscriber, reg, event)

        # test that removal succeeds with Registered status
        reg.status = RegisteredStatus
        SimpleRegistrationRemoveSubscriber(reg, event)

        self.assertEquals(reg.status, UnregisteredStatus)

class TestSimpleRegistration(TestCase):

    def setUp(self):
        # XXX: May need more setup related to Adapter service?
        # We can't use the status property on a SimpleRegistration instance.
        # we disable it for these tests
        self.__oldprop = SimpleRegistration.status
        del SimpleRegistration.status

    def tearDown(self):
        # Restore the status prop
        SimpleRegistration.status = self.__oldprop

class TestComponentRegistration(TestSimpleRegistration, PlacefulSetup):

    def setUp(self):
        TestSimpleRegistration.setUp(self)
        PlacefulSetup.setUp(self, site=True)
        self.name = 'foo'

    def test_component(self):
        # set up a component
        component = object()
        # set up a registration
        cfg = ComponentRegistration(component)
        # check that getComponent finds the registration
        self.assertEquals(cfg.component, component)

    def test_getComponent_permission(self):
        # set up a component
        component = object()
        # set up a registration
        cfg = ComponentRegistration(component, 'zope.TopSecret')
        cfg.getInterface = lambda: ITestComponent
        # Check that the component is proxied.
        result = cfg.component
        self.assertEquals(result, component)
        self.failUnless(type(result) is Proxy)

class TestComponentRegistrationEvents(object):
    def test_addNotify(self):
        """
        First we create a dummy registration

          >>> reg = DummyRegistration()

        Now call notification

          >>> ComponentRegistrationAddSubscriber(reg, None)

        Check to make sure the adapter added the path

          >>> reg.dependents()
          ('dummy!',)
        """

    def test_removeNotify_dependents(self):
        """
        First we create a dummy registration

          >>> reg = DummyRegistration()

        Now call notification

          >>> ComponentRegistrationAddSubscriber(reg, None)

        Check to make sure the adapter added the path

          >>> reg.dependents()
          ('dummy!',)

        Now remove notify:

          >>> ComponentRegistrationRemoveSubscriber(reg, None)

        Check to make sure the adapter removed the dependencie(s).

          >>> reg.dependents()
          ()

        """

class TestRegisterableEvents(object):
    """Tests handling of registered component rename.

    >>> sm = PlacefulSetup().setUp(site=True)

    We'll first add a registerable component to the default site management
    folder:

        >>> component = DummyRegisterable()
        >>> sm['default']['foo'] = component

    and create a registration for it:

        >>> reg = ComponentRegistration(component)
        >>> sm['default']['reg'] = reg
        >>> ztapi.provideAdapter(IRegisterable, IRegistered, Registered)
        >>> IRegistered(component).addUsage('reg')

    The registration is initially configured with the component path:

        >>> reg.component is component
        True

    The RegisterableMoveSubscriber subscriber is for IRegisterable and
    IObjectMovedEvent. When we invoke it with the appropriate 'rename' event
    (i.e. oldParent is the same as newParent):

        >>> event = ObjectMovedEvent(component,
        ...     oldParent=sm['default'],
        ...     oldName='foo',
        ...     newParent=sm['default'],
        ...     newName='bar')
        >>> RegisterableMoveSubscriber(component, event)

    the registration component path is updated accordingly:

        >>> reg.component is component
        True

    However, if we invoke RegisterableMoveSubscriber with a 'move' event (i.e.
    oldParent is different from newParent):

        >>> event = ObjectMovedEvent(component,
        ...     oldParent=sm['default'],
        ...     oldName='foo',
        ...     newParent=object(),
        ...     newName='foo')
        >>> RegisterableMoveSubscriber(component, event)
        Traceback (most recent call last):
        DependencyError: Can't move a registered component from its container.

    >>> PlacefulSetup().tearDown()
    """

class TestRegisterableCopier(object):
    """Tests the copier for registerable components.

    >>> sm = PlacefulSetup().setUp(site=True)

    Registered components have annotation noting which registrations are
    currently using the component. Copied components should not be noted
    as used.

    RegisterableCopier is used instead of the default object copier to
    ensure that such usages are removed from the copied component.

    To illustrate, we'll setup a component in the default site management
    folder:

        >>> component = DummyRegisterable()
        >>> sm['default']['foo'] = component

    and create a registration for it:

        >>> reg = ComponentRegistration(component)
        >>> sm['default']['reg'] = reg
        >>> ztapi.provideAdapter(IRegisterable, IRegistered, Registered)
        >>> IRegistered(component).addUsage('/++etc++site/default/reg')

    Note the current usages for the component:

        >>> IRegistered(component).usages()
        (u'/++etc++site/default/reg',)

    Using RegisterableCopier, we can make a copy of the component:

        >>> copier = RegisterableCopier(component)
        >>> copier.copyTo(sm['default'], 'bar')
        'bar'

    The copied component is not used:

        >>> copy = sm['default']['bar']
        >>> IRegistered(copy).usages()
        ()

    >>> PlacefulSetup().tearDown()
    """

def test_suite():
    return TestSuite((
        makeSuite(TestSimpleRegistration),
        makeSuite(TestComponentRegistration),
        makeSuite(TestSimpleRegistrationEvents),
        DocTestSuite(),
        DocTestSuite('zope.app.registration.registration',
                     setUp=placelesssetup.setUp,
                     tearDown=placelesssetup.tearDown,
                     globs={'subscribe': ztapi.subscribe}),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
