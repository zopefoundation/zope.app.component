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
"""Local Adapter and Service Tests

$Id$
"""
import unittest
import zope.interface
from transaction import get_transaction
from ZODB.tests.util import DB

from zope.testing.doctestunit import DocTestSuite
from zope.interface.adapter import AdapterRegistry
from zope.component.adapter import GlobalAdapterService

from zope.app import zapi
from zope.app.adapter.adapter import LocalAdapterRegistry, LocalAdapterService
from zope.app.registration.interfaces import RegisteredStatus

class IF0(zope.interface.Interface):
    pass

class IF1(IF0):
    pass

class IF2(IF1):
    pass

class IB0(zope.interface.Interface):
    pass

class IB1(IB0):
    pass

class IR0(zope.interface.Interface):
    pass

class IR1(IR0):
    pass

class R1(object):
    zope.interface.implements(IR1)

class F0(object):
    zope.interface.implements(IF0)

class F2(object):
    zope.interface.implements(IF2)

class Registration(object):
    name=u''
    with=()
    provided=zope.interface.Interface
    required=None
    
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __repr__(self):
        return "Registration(%r, %s, %r, %r, %r)" % (
            getattr(self.required, '__name__', None),
            tuple([i.__name__ for i in self.with]),
            self.provided.__name__, self.name, self.factory
            )
    

    def factories(self):
        return self.factory,
    factories = property(factories)

# Create a picklable global registry. The pickleability of other
# global adapter registries is beyond the scope of these tests:
class GlobalAdapterRegistry(AdapterRegistry):
    def __reduce__(self):
        return 'globalAdapterRegistry'

globalAdapterRegistry = GlobalAdapterRegistry()

class TestStack(object):
    registration = None
    registrations = ()

    def __init__(self, parent):
        self.__parent__ = parent

    def active(self):
        return self.registration

    def info(self):
        for registration in self.registrations:
            yield {'registration': registration}

    def activate(self, registration):
        self.registration = registration
        if registration not in self.registrations:
            self.registrations += (registration,)
        self.__parent__.notifyActivated(self, registration)

    def deactivate(self, registration):
        self.registration = None
        self.__parent__.notifyDeactivated(self, registration)


class LocalAdapterRegistry(LocalAdapterRegistry):
    """For testing, use custom stack type
    """
    _stackType = TestStack


def test_local_adapter():
    """Local Adapter Tests

   Local surrogates and adapter registries share declarations with
   those "above" them.

   Suppose we have a global AdapterRegistry:

   >>> G = AdapterRegistry()

   we also have a local adapter registry, with G as it's base:

   >>> L1 = LocalAdapterRegistry(G)

   and so on:

   >>> L2 = LocalAdapterRegistry(G, L1)

   Now, if we declare an adapter globally:

   >>> G.register([IF1], IB1, '', 'A11G')

   we can query it locally:

   >>> L1.lookup([IF2], IB1)
   'A11G'
   
   >>> L2.lookup([IF2], IB1)
   'A11G'

   We can add local definitions:

   >>> ra011 = Registration(required = IF0, provided=IB1, factory='A011')
   >>> L1.createRegistrationsFor(ra011).activate(ra011)

   and use it:

   >>> L1.lookup([IF0], IB1)
   'A011'
   
   >>> L2.lookup([IF0], IB1)
   'A011'
   
   but not outside L1:

   >>> G.lookup([IF0], IB1)

   Note that it doesn't override the non-local adapter:

   >>> L1.lookup([IF2], IB1)
   'A11G'
   
   >>> L2.lookup([IF2], IB1)
   'A11G'
   
   because it was more specific.

   Let's override the adapter in L2:

   >>> ra112 = Registration(required = IF1, provided=IB1, factory='A112')
   >>> L2.createRegistrationsFor(ra112).activate(ra112)

   Now, in L2, we get the new adapter, because it's as specific and more
   local than the one from G:

   >>> L2.lookup([IF2], IB1)
   'A112'
   
   But we still get the old one in L1

   >>> L1.lookup([IF2], IB1)
   'A11G'
   
   Note that we can ask for less specific interfaces and still get the adapter:

   >>> L2.lookup([IF2], IB0)
   'A112'

   >>> L1.lookup([IF2], IB0)
   'A11G'

   We get the more specific adapter even if there is a less-specific
   adapter to B0:

   >>> G.register([IF1], IB1, '', 'A10G')

   >>> L2.lookup([IF2], IB0)
   'A112'

   But if we have an equally specific and equally local adapter to B0, it
   will win:

   >>> ra102 = Registration(required = IF1, provided=IB0, factory='A102')
   >>> L2.createRegistrationsFor(ra102).activate(ra102)

   >>> L2.lookup([IF2], IB0)
   'A102'

   We can deactivate registrations, which has the effect of deleting adapters:


   >>> L2.queryRegistrationsFor(ra112).deactivate(ra112)

   >>> L2.lookup([IF2], IB0)
   'A102'

   >>> L2.lookup([IF2], IB1)
   'A10G'

   >>> L2.queryRegistrationsFor(ra102).deactivate(ra102)

   >>> L2.lookup([IF2], IB0)
   'A10G'

   We can ask for all of the registrations :

   >>> registrations = list(L1.registrations())
   >>> registrations
   [Registration('IF0', (), 'IB1', u'', 'A011')]

   This shows only the local registrations in L1.
   """

def test_named_adapters():
    """
    Suppose we have a global AdapterRegistry:

    >>> G = AdapterRegistry()

    we also have a local adapter registry, with G as it's base:

    >>> L1 = LocalAdapterRegistry(G)

    and so on:

    >>> L2 = LocalAdapterRegistry(G, L1)

    Now, if we declare an adapter globally:

    >>> G.register([IF1], IB1, 'bob', 'A11G')

    we can query it locally:

    >>> L1.lookup([IF2], IB1)
    >>> L1.lookup([IF2], IB1, 'bob')
    'A11G'

    >>> L2.lookup([IF2], IB1)
    >>> L2.lookup([IF2], IB1, 'bob')
    'A11G'

    We can add local definitions:

    >>> ra011 = Registration(required = IF0, provided=IB1, factory='A011',
    ...                      name='bob')
    >>> L1.createRegistrationsFor(ra011).activate(ra011)
    
    and use it:

    >>> L1.lookup([IF0], IB1)
    >>> L1.lookup([IF0], IB1, 'bob')
    'A011'

    >>> L2.lookup([IF0], IB1)
    >>> L2.lookup([IF0], IB1, 'bob')
    'A011'

    but not outside L1:

    >>> G.lookup([IF0], IB1, 'bob')

    Note that it doesn't override the non-local adapter:

    >>> L1.lookup([IF2], IB1)
    >>> L1.lookup([IF2], IB1, 'bob')
    'A11G'

    >>> L2.lookup([IF2], IB1)
    >>> L2.lookup([IF2], IB1, 'bob')
    'A11G'

    because it was more specific.

    Let's override the adapter in L2:

    >>> ra112 = Registration(required = IF1, provided=IB1, factory='A112',
    ...                      name='bob')
    >>> L2.createRegistrationsFor(ra112).activate(ra112)

    Now, in L2, we get the new adapter, because it's as specific and more
    local than the one from G:

    >>> L2.lookup([IF2], IB1)
    >>> L2.lookup([IF2], IB1, 'bob')
    'A112'

    But we still get thye old one in L1

    >>> L1.lookup([IF2], IB1)
    >>> L1.lookup([IF2], IB1, 'bob')
    'A11G'

    Note that we can ask for less specific interfaces and still get the adapter:

    >>> L2.lookup([IF2], IB0)
    >>> L2.lookup([IF2], IB0, 'bob')
    'A112'

    >>> L1.lookup([IF2], IB0)
    >>> L1.lookup([IF2], IB0, 'bob')
    'A11G'

    We get the more specific adapter even if there is a less-specific
    adapter to B0:

    >>> G.register([IF1], IB1, 'bob', 'A10G')

    >>> L2.lookup([IF2], IB0)
    >>> L2.lookup([IF2], IB0, 'bob')
    'A112'

    But if we have an equally specific and equally local adapter to B0, it
    will win:

    >>> ra102 = Registration(required = IF1, provided=IB0, factory='A102',
    ...                      name='bob')
    >>> L2.createRegistrationsFor(ra102).activate(ra102)
    
    >>> L2.lookup([IF2], IB0)
    >>> L2.lookup([IF2], IB0, 'bob')
    'A102'

    We can deactivate registrations, which has the effect of deleting adapters:


    >>> L2.queryRegistrationsFor(ra112).deactivate(ra112)

    >>> L2.lookup([IF2], IB0)
    >>> L2.lookup([IF2], IB0, 'bob')
    'A102'

    >>> L2.lookup([IF2], IB1)
    >>> L2.lookup([IF2], IB1, 'bob')
    'A10G'

    >>> L2.queryRegistrationsFor(ra102).deactivate(ra102)

    >>> L2.lookup([IF2], IB0)
    >>> L2.lookup([IF2], IB0, 'bob')
    'A10G'
    """

def test_multi_adapters():
    """
    Suppose we have a global AdapterRegistry:

    >>> G = AdapterRegistry()

    we also have a local adapter registry, with G as it's base:

    >>> L1 = LocalAdapterRegistry(G)

    and so on:

    >>> L2 = LocalAdapterRegistry(G, L1)

    Now, if we declare an adapter globally:

    >>> G.register([IF1, IR0], IB1, 'bob', 'A11G')

    we can query it locally:

    >>> L1.lookup([IF2, IR1], IB1, 'bob')
    'A11G'

    >>> L2.lookup([IF2, IR1], IB1, 'bob')
    'A11G'

    We can add local definitions:

    >>> ra011 = Registration(required = IF0, provided=IB1, factory='A011',
    ...                      name='bob', with=(IR0,))
    >>> L1.createRegistrationsFor(ra011).activate(ra011)
    
    and use it:

    >>> L1.lookup([IF0, IR1], IB1, 'bob')
    'A011'

    >>> L2.lookup([IF0, IR1], IB1, 'bob')
    'A011'

    but not outside L1:

    >>> G.lookup((IF0, IR1), IB1, 'bob')

    Note that it doesn't override the non-local adapter:

    >>> L1.lookup([IF2, IR1], IB1, 'bob')
    'A11G'

    >>> L2.lookup((IF2, IR1), IB1, 'bob')
    'A11G'

    because it was more specific.

    Let's override the adapter in L2:

    >>> ra112 = Registration(required = IF1, provided=IB1, factory='A112',
    ...                      name='bob', with=(IR0,))
    >>> L2.createRegistrationsFor(ra112).activate(ra112)

    Now, in L2, we get the new adapter, because it's as specific and more
    local than the one from G:

    >>> L2.lookup((IF2, IR1), IB1, 'bob')
    'A112'

    But we still get the old one in L1

    >>> L1.lookup((IF2, IR1), IB1, 'bob')
    'A11G'

    Note that we can ask for less specific interfaces and still get
    the adapter:

    >>> L2.lookup((IF2, IR1), IB0, 'bob')
    'A112'

    >>> L1.lookup((IF2, IR1), IB0, 'bob')
    'A11G'

    We get the more specific adapter even if there is a less-specific
    adapter to B0:

    >>> G.register([IF1, IR0], IB1, 'bob', 'A10G')

    >>> L2.lookup((IF2, IR1), IB0, 'bob')
    'A112'

    But if we have an equally specific and equally local adapter to B0, it
    will win:

    >>> ra102 = Registration(required = IF1, provided=IB0, factory='A102',
    ...                      name='bob', with=(IR0,))
    >>> L2.createRegistrationsFor(ra102).activate(ra102)
    
    >>> L2.lookup((IF2, IR1), IB0, 'bob')
    'A102'

    We can deactivate registrations, which has the effect of deleting adapters:

    >>> L2.queryRegistrationsFor(ra112).deactivate(ra112)

    >>> L2.lookup((IF2, IR1), IB0, 'bob')
    'A102'

    >>> L2.lookup((IF2, IR1), IB1, 'bob')
    'A10G'

    >>> L2.queryRegistrationsFor(ra102).deactivate(ra102)

    >>> L2.lookup([IF2], IB0)
    >>> L2.lookup((IF2, IR1), IB0, 'bob')
    'A10G'
    """

def test_persistence():
    """
    >>> db = DB()
    >>> conn1 = db.open()

    >>> G = globalAdapterRegistry
    >>> L1 = LocalAdapterRegistry(G)
    >>> L2 = LocalAdapterRegistry(G, L1)

    >>> conn1.root()['L1'] = L1
    >>> conn1.root()['L2'] = L2
    
    >>> G.register([IF1], IB1, 'bob', 'A11G')
    >>> L1.lookup([IF2], IB1)
    >>> L1.lookup([IF2], IB1, 'bob')
    'A11G'

    >>> L2.lookup([IF2], IB1)
    >>> L2.lookup([IF2], IB1, 'bob')
    'A11G'

    We can add local definitions:

    >>> ra011 = Registration(required = IF0, provided=IB1, factory='A011',
    ...                      name='bob')
    >>> L1.createRegistrationsFor(ra011).activate(ra011)

    and use it:

    >>> L1.lookup([IF0], IB1)
    >>> L1.lookup([IF0], IB1, 'bob')
    'A011'

    >>> L2.lookup([IF0], IB1)
    >>> L2.lookup([IF0], IB1, 'bob')
    'A011'

    but not outside L1:

    >>> G.lookup([IF0], IB1)

    Note that it doesn't override the non-local adapter:

    >>> L1.lookup([IF2], IB1)
    >>> L1.lookup([IF2], IB1, 'bob')
    'A11G'

    >>> L2.lookup([IF2], IB1)
    >>> L2.lookup([IF2], IB1, 'bob')
    'A11G'

    because it was more specific.

    Let's override the adapter in L2:

    >>> ra112 = Registration(required = IF1, provided=IB1, factory='A112',
    ...                      name='bob')
    >>> L2.createRegistrationsFor(ra112).activate(ra112)

    Now, in L2, we get the new adapter, because it's as specific and more
    local than the one from G:

    >>> L2.lookup([IF2], IB1)
    >>> L2.lookup([IF2], IB1, 'bob')
    'A112'

    But we still get the old one in L1

    >>> L1.lookup([IF2], IB1)
    >>> L1.lookup([IF2], IB1, 'bob')
    'A11G'

    Note that we can ask for less specific interfaces and still get
    the adapter:

    >>> L2.lookup([IF2], IB0)
    >>> L2.lookup([IF2], IB0, 'bob')
    'A112'

    >>> L1.lookup([IF2], IB0)
    >>> L1.lookup([IF2], IB0, 'bob')
    'A11G'

    We get the more specific adapter even if there is a less-specific
    adapter to B0:

    >>> G.register([IF0], IB0, 'bob', 'A00G')

    >>> L2.lookup([IF2], IB0)
    >>> L2.lookup([IF2], IB0, 'bob')
    'A112'

    But if we have an equally specific and equally local adapter to B0, it
    will win:

    >>> ra102 = Registration(required = IF1, provided=IB0, factory='A102',
    ...                      name='bob')
    >>> L2.createRegistrationsFor(ra102).activate(ra102)

    >>> L2.lookup([IF2], IB0)
    >>> L2.lookup([IF2], IB0, 'bob')
    'A102'

    >>> L1.lookup([IF2], IB0, 'bob')
    'A11G'
    >>> L1.lookup([IF2], IB1, 'bob')
    'A11G'
    >>> L2.lookup([IF2], IB0, 'bob')
    'A102'
    >>> L2.lookup([IF2], IB1, 'bob')
    'A112'

    >>> get_transaction().commit()

    Now, let's open another transaction:

    >>> conn2 = db.open()

    >>> L1 = conn2.root()['L1']
    >>> L2 = conn2.root()['L2']

    We should get the same outputs:

    >>> L1.lookup([IF2], IB0, 'bob')
    'A11G'
    >>> L1.lookup([IF2], IB1, 'bob')
    'A11G'
    >>> L2.lookup([IF2], IB0, 'bob')
    'A102'
    >>> L2.lookup([IF2], IB1, 'bob')
    'A112'
    
    We can deactivate registrations, which has the effect of deleting adapters:

    >>> L2.queryRegistrationsFor(ra112).deactivate(ra112)
    >>> L2.queryRegistrationsFor(ra102).deactivate(ra102)

    >>> L1.lookup([IF2], IB0, 'bob')
    'A11G'
    >>> L1.lookup([IF2], IB1, 'bob')
    'A11G'
    >>> L2.lookup([IF2], IB0, 'bob')
    'A11G'
    >>> L2.lookup([IF2], IB1, 'bob')
    'A11G'

    >>> get_transaction().commit()

    If we look back at the first connection, we should get the same data:

    >>> conn1.sync()
    >>> L1 = conn1.root()['L1']
    >>> L2 = conn1.root()['L2']

    We should see the result of the deactivations:
    
    >>> L1.lookup([IF2], IB0, 'bob')
    'A11G'
    >>> L1.lookup([IF2], IB1, 'bob')
    'A11G'
    >>> L2.lookup([IF2], IB0, 'bob')
    'A11G'
    >>> L2.lookup([IF2], IB1, 'bob')
    'A11G'

    Cleanup:
    >>> G.__init__()
    >>> db.close()
    """


def test_local_default():
    """
    >>> G = AdapterRegistry()
    >>> L1 = LocalAdapterRegistry(G)
    >>> r = Registration(required = None, provided=IB1, factory='Adapter')
    >>> L1.createRegistrationsFor(r).activate(r)
    >>> L1.lookup([IF2], IB1)
    'Adapter'
    """


def test_changing_next():
    """
    >>> G = AdapterRegistry()
    >>> L1 = LocalAdapterRegistry(G)
    >>> L2 = LocalAdapterRegistry(G, L1)
    >>> f2 = F2()

    >>> L2.lookup([IF2], IB1)

    >>> G.register([IF1], IB1, '', 'A11G')
    >>> L2.lookup([IF2], IB1)
    'A11G'


    >>> ra111 = Registration(required = IF1, provided=IB1, factory='A111')
    >>> L1.createRegistrationsFor(ra111).activate(ra111)
    >>> L2.lookup([IF2], IB1)
    'A111'

    >>> L1.next
    >>> L2.next == L1
    True
    >>> L1.subs == (L2,)
    True
    >>> L3 = LocalAdapterRegistry(G, L1)
    >>> L2.setNext(L3)
    >>> L2.next == L3
    True
    >>> L3.next == L1
    True
    >>> L1.subs == (L3,)
    True
    >>> L3.subs == (L2,)
    True

    >>> ra113 = Registration(required = IF1, provided=IB1, factory='A113')
    >>> L3.createRegistrationsFor(ra113).activate(ra113)

    >>> L2.lookup([IF2], IB1)
    'A113'
    >>> L2.setNext(L1)
    >>> L2.next == L1
    True
    >>> L3.next == L1
    True
    >>> L1.subs == (L3, L2)
    True
    >>> L3.subs == ()
    True
    >>> L2.lookup([IF2], IB1)
    'A111'

    """

def test_LocalAdapterBasedService():
    """
    Setup folders and service managers:
    
    >>> from zope.app.tests import setup
    >>> setup.placefulSetUp()
    >>> root = setup.buildSampleFolderTree()
    >>> sm = setup.createServiceManager(root)
    >>> sm1 = setup.createServiceManager(root['folder1'])
    >>> sm1_1 = setup.createServiceManager(root['folder1']['folder1_1'])
    >>> sm1_1_1 = setup.createServiceManager(
    ...                         root['folder1']['folder1_1']['folder1_1_1'])

    Define the service

    >>> gsm = zapi.getGlobalServices()
    >>> gsm.defineService('F', IF1)

    Create the global service

    >>> g = F2()
    >>> gsm.provideService('F', g)

    Create a local service class, which must define setNext:

    >>> import zope.app.site.interfaces
    >>> from zope.app.adapter.adapter import LocalAdapterBasedService
    >>> class LocalF(LocalAdapterBasedService):
    ...     zope.interface.implements(
    ...         IF2,
    ...         zope.app.site.interfaces.ISimpleService,
    ...         )
    ...     def setNext(self, next, global_):
    ...         self.next, self.global_ = next, global_

    If we add a local service, It gets it's next and global_ attrs set:

    >>> f1 = LocalF()
    >>> hasattr(f1, 'next') or hasattr(f1, 'global_')
    False
    >>> setup.addService(sm1, 'F', f1) is f1
    True
    >>> (f1.next, f1.global_) == (None, g)
    True

    If we add another service below, it's next will point to the one
    above:
    
    >>> f1_1_1 = LocalF()
    >>> setup.addService(sm1_1_1, 'F', f1_1_1) is f1_1_1
    True
    >>> (f1_1_1.next, f1_1_1.global_) == (f1, g)
    True

    We can insert a service in an intermediate site:
    
    >>> f1_1 = LocalF()
    >>> setup.addService(sm1_1, 'F', f1_1) is f1_1
    True
    >>> (f1_1.next, f1_1.global_) == (f1, g)
    True
    >>> (f1_1_1.next, f1_1_1.global_) == (f1_1, g)
    True

    Deactivating services adjust the relevant next pointers

    >>> default = zapi.traverse(sm1_1, 'default')
    >>> rm = default.getRegistrationManager()
    >>> rm.values()[0].status = RegisteredStatus
    >>> (f1_1_1.next, f1_1_1.global_) == (f1, g)
    True

    >>> default = zapi.traverse(sm1, 'default')
    >>> rm = default.getRegistrationManager()
    >>> rm.values()[0].status = RegisteredStatus
    >>> (f1_1_1.next, f1_1_1.global_) == (None, g)
    True
    
    >>> setup.placefulTearDown()
    """

def test_service_registrations():
    """
    Local Adapter Service Registration Tests


    Local adapter services share declarations and registrations with those
    "above" them.

    Suppose we have a global adapter service, which is a type of
    adapter registry that is an zope.component.interfaces.IRegistry:

    >>> G = GlobalAdapterService()

    we also have a local adapter registry, with G as it's base:
    
    >>> L1 = LocalAdapterService(G)
    
    and another local, with G as it's base:

    >>> L2 = LocalAdapterService(G)
    
    and L1 as it's next service:
    
    >>> L2.setNext(L1)
    
    Now will register some adapters:
    
    >>> G.register([IF1], IB1, '', 'A11G')
    >>> ra011 = Registration(required = IF0, provided=IB1, factory='A011')
    >>> L1.createRegistrationsFor(ra011).register(ra011)
    >>> ra112 = Registration(required = IF1, provided=IB1, factory='A112')
    >>> L2.createRegistrationsFor(ra112).register(ra112)
    >>> ra102 = Registration(required = IF1, provided=IB0, factory='A102')
    >>> L2.createRegistrationsFor(ra102).register(ra102)
    
    We can ask for all of the registrations locally:
    
    >>> registrations = map(repr, L1.registrations())
    >>> registrations.sort()
    >>> for registration in registrations:
    ...     print registration
    AdapterRegistration(('IF1',), 'IB1', '', 'A11G', '')
    Registration('IF0', (), 'IB1', u'', 'A011')
    
    This shows the local registrations in L1 and the global registrations.
    
    If we ask L2, we'll see the registrations from G, L1, and L2:
    
    >>> registrations = map(repr, L2.registrations())
    >>> registrations.sort()
    >>> for registration in registrations:
    ...     print registration
    AdapterRegistration(('IF1',), 'IB1', '', 'A11G', '')
    Registration('IF0', (), 'IB1', u'', 'A011')
    Registration('IF1', (), 'IB0', u'', 'A102')
    Registration('IF1', (), 'IB1', u'', 'A112')
    
    Now we just want the local registrations for L1:
    
    >>> registrations = map(repr, L1.registrations(localOnly=True))
    >>> registrations.sort()
    >>> for registration in registrations:
    ...     print registration
    Registration('IF0', (), 'IB1', u'', 'A011')

    """
    
def test_suite():
    return unittest.TestSuite((
        DocTestSuite(),
        ))

if __name__ == '__main__': unittest.main()
