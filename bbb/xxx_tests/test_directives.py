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
"""Component Directives Tests

$Id$
"""
import re
import unittest
import pprint
from cStringIO import StringIO

from zope.interface import Interface, implements
from zope.testing.doctestunit import DocTestSuite
from zope.app.component.metaconfigure import interface
from zope.app.content.interfaces import IContentType

from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.configuration.exceptions import ConfigurationError

from zope.security.proxy import removeSecurityProxy
from zope.security.proxy import getTestProxyItems

import zope.app.component
from zope.component.exceptions import ComponentLookupError

from zope.app import zapi
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.component.tests.views import IV, IC, V1, VZMI, R1, RZMI, IR
from zope.component.tests.request import Request
from zope.security.checker import ProxyFactory

# TODO: tests for other directives needed

atre = re.compile(' at [0-9a-fA-Fx]+')

class Context(object):
    actions = ()
    
    def action(self, discriminator, callable, args):
        self.actions += ((discriminator, callable, args), )

    def __repr__(self):
        stream = StringIO()
        pprinter = pprint.PrettyPrinter(stream=stream, width=60)
        pprinter.pprint(self.actions)
        r = stream.getvalue()
        return (''.join(atre.split(r))).strip()


def testInterface():
    """
    >>> context = Context()
    >>> class I(Interface):
    ...     pass
    >>> IContentType.providedBy(I)
    False
    >>> interface(context, I, IContentType)
    >>> context
    ((None,
      <function provideInterface>,
      ('',
       <InterfaceClass zope.app.component.tests.test_directives.I>,
       <InterfaceClass zope.app.content.interfaces.IContentType>)),)
    >>> from zope.interface.interfaces import IInterface
    >>> IContentType.extends(IInterface)
    True
    >>> IInterface.providedBy(I)
    True
    """

template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:test='http://www.zope.org/NS/Zope3/test'
   i18n_domain='zope'>
   %s
   </configure>"""

class Ob(object):
    implements(IC)

def definePermissions():
    XMLConfig('meta.zcml', zope.app.component)()

class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(Test, self).setUp()
        XMLConfig('meta.zcml', zope.app.component)()
        XMLConfig('meta.zcml', zope.app.security)()

    def testSubscriber(self):
        from zope.app.component.tests.adapter import A1, A2, A3, I3
        from zope.app.component.tests.adapter import IS
        from zope.component.tests.components import Content

        xmlconfig(StringIO(template % (
            """
            <subscriber
              provides="zope.app.component.tests.adapter.IS"
              factory="zope.app.component.tests.adapter.A3"
              for="zope.component.tests.components.IContent
                   zope.app.component.tests.adapter.I1"
              />
            """
            )))

        content = Content()
        a1 = A1()
        subscribers = zapi.subscribers((content, a1), IS)

        a3 = subscribers[0]

        self.assertEqual(a3.__class__, A3)
        self.assertEqual(a3.context, (content, a1))

    def testTrustedSubscriber(self):
        from zope.app.component.tests.adapter import A1, A2, A3, I3
        from zope.app.component.tests.adapter import IS
        from zope.component.tests.components import Content

        xmlconfig(StringIO(template % (
            """
            <subscriber
              provides="zope.app.component.tests.adapter.IS"
              factory="zope.app.component.tests.adapter.A3"
              for="zope.component.tests.components.IContent
                   zope.app.component.tests.adapter.I1"
              trusted="yes"
              />
            """
            )))

        # With an unproxied object, business as usual
        content = Content()
        a1 = A1()
        subscribers = zapi.subscribers((content, a1), IS)

        a3 = subscribers[0]

        self.assertEqual(a3.__class__, A3)
        self.assertEqual(a3.context, (content, a1))

        # Now with a proxied object:
        from zope.security.checker import ProxyFactory
        p = ProxyFactory(content)

        # we get a proxied subscriber:
        a3 = zapi.subscribers((p, a1), IS)[0]
        from zope.security.proxy import Proxy
        self.assertEqual(type(a3), Proxy)


        # around an unproxied object:
        from zope.security.proxy import removeSecurityProxy
        self.assert_(removeSecurityProxy(a3).context[0] is content)

    def testSubscriber_w_no_provides(self):
        from zope.app.component.tests.adapter import A1, A2, Handler, I3
        from zope.component.tests.components import Content

        xmlconfig(StringIO(template % (
            """
            <subscriber
              for="zope.component.tests.components.IContent
                   zope.app.component.tests.adapter.I1"
              factory="zope.app.component.tests.adapter.Handler"
              />
            """
            )))

        content = Content()
        a1 = A1()
        list(zapi.subscribers((content, a1), None))

        self.assertEqual(content.args, ((a1,),))
        
    def testMultiSubscriber(self):
        from zope.app.component.tests.adapter import A1, A2, A3, I3
        from zope.app.component.tests.adapter import IS
        from zope.component.tests.components import Content

        xmlconfig(StringIO(template % (
            """
            <subscriber
              provides="zope.app.component.tests.adapter.IS"
              factory="zope.app.component.tests.adapter.A3"
              for="zope.component.tests.components.IContent
                   zope.app.component.tests.adapter.I1"
              />
            <subscriber
              provides="zope.app.component.tests.adapter.IS"
              factory="zope.app.component.tests.adapter.A2"
              for="zope.component.tests.components.IContent
                   zope.app.component.tests.adapter.I1"
              />
            """
            )))

        content = Content()
        a1 = A1()
        subscribers = zapi.subscribers((content, a1), IS)

        expectedLength = 2
        self.assertEqual(len(subscribers), expectedLength)
        classesNotFound = [A2, A3]
        for a in subscribers:
            classesNotFound.remove(a.__class__)
        self.failIf(classesNotFound)

    def testAdapter(self):
        # Full import is critical!
        from zope.component.tests.components import Content, IApp, Comp

        self.assertEqual(IV(Content(), None), None)

        xmlconfig(StringIO(template % (
            """
            <adapter
              factory="zope.component.tests.components.Comp"
              provides="zope.component.tests.components.IApp"
              for="zope.component.tests.components.IContent"
              />
            """
            )))

        self.assertEqual(IApp(Content()).__class__, Comp)

    def testTrustedAdapter(self):
        # Full import is critical!
        from zope.component.tests.components import Content
        from zope.app.component.tests.adapter import A1, I1

        xmlconfig(StringIO(template % (
            """
            <adapter
              factory="zope.app.component.tests.adapter.A1"
              provides="zope.app.component.tests.adapter.I1"
              for="zope.component.tests.components.IContent"
              trusted="yes"
              />
            """
            )))

        # With an unproxied object, business as usual
        ob = Content()
        self.assertEqual(type(I1(ob)), type(A1()))

        # Now with a proxied object:
        from zope.security.checker import ProxyFactory
        p = ProxyFactory(ob)

        # we get a proxied adapter:
        a = I1(p)
        from zope.security.proxy import Proxy
        self.assertEqual(type(a), Proxy)

        # around an unproxied object:
        from zope.security.proxy import removeSecurityProxy
        a = removeSecurityProxy(a)
        self.assert_(a.context[0] is ob)
        
        

    def testAdapter_w_multiple_factories(self):
        from zope.app.component.tests.adapter import A1, A2, A3
        from zope.component.tests.components import Content, IApp

        xmlconfig(StringIO(template % (
            """
            <adapter
              factory="zope.app.component.tests.adapter.A1
                       zope.app.component.tests.adapter.A2
                       zope.app.component.tests.adapter.A3
                      "
              provides="zope.component.tests.components.IApp"
              for="zope.component.tests.components.IContent"
              />
            """
            )))

        # The resulting adapter should be an A3, around an A2, around
        # an A1, andround the content:

        content = Content()
        a3 = IApp(content)
        self.assertEqual(a3.__class__, A3)
        a2 = a3.context[0]
        self.assertEqual(a2.__class__, A2)
        a1 = a2.context[0]
        self.assertEqual(a1.__class__, A1)
        self.assertEqual(a1.context[0], content)

    def testAdapter_fails_w_no_factories(self):
        self.assertRaises(ConfigurationError,
                          xmlconfig,
                          StringIO(template % (
                             """
                             <adapter
                             factory="
                                     "
                             provides="zope.component.tests.components.IApp"
                             for="zope.component.tests.components.IContent"
                             />
                             """
                             )),
                          )

    def testMultiAdapter(self):
        from zope.app.component.tests.adapter import A1, A2, A3, I3
        from zope.component.tests.components import Content

        xmlconfig(StringIO(template % (
            """
            <adapter
              factory="zope.app.component.tests.adapter.A3
                      "
              provides="zope.app.component.tests.adapter.I3"
              for="zope.component.tests.components.IContent
                   zope.app.component.tests.adapter.I1
                   zope.app.component.tests.adapter.I2
                  "
              />
            """
            )))

        content = Content()
        a1 = A1()
        a2 = A2()
        a3 = zapi.queryMultiAdapter((content, a1, a2), I3)
        self.assertEqual(a3.__class__, A3)
        self.assertEqual(a3.context, (content, a1, a2))

    def testNullAdapter(self):
        from zope.app.component.tests.adapter import A3, I3

        xmlconfig(StringIO(template % (
            """
            <adapter
              factory="zope.app.component.tests.adapter.A3
                      "
              provides="zope.app.component.tests.adapter.I3"
              for=""
              />
            """
            )))

        a3 = zapi.queryMultiAdapter((), I3)
        self.assertEqual(a3.__class__, A3)
        self.assertEqual(a3.context, ())

    def testMultiAdapterFails_w_multiple_factories(self):
        self.assertRaises(ConfigurationError,
                          xmlconfig,
                          StringIO(template % (
                             """
                             <adapter
                             factory="zope.app.component.tests.adapter.A1
                                      zope.app.component.tests.adapter.A2
                                     "
                             for="zope.component.tests.components.IContent
                                  zope.app.component.tests.adapter.I1
                                  zope.app.component.tests.adapter.I2
                                  "
                             provides="zope.component.tests.components.IApp"
                             />
                             """
                             )),
                          )
        
        self.assertRaises(ConfigurationError,
                          xmlconfig,
                          StringIO(template % (
                             """
                             <adapter
                             factory="zope.app.component.tests.adapter.A1
                                      zope.app.component.tests.adapter.A2
                                     "
                             for=""
                             provides="zope.component.tests.components.IApp"
                             />
                             """
                             )),
                          )
        

    def testNamedAdapter(self):


        # Full import is critical!
        from zope.component.tests.components import Content, IApp, Comp

        self.testAdapter()
        self.assertEqual(IApp(Content()).__class__, Comp)
        self.assertEqual(zapi.queryAdapter(Content(), IV, 'test'), None)

        xmlconfig(StringIO(template % (
            """
            <adapter
              factory="zope.component.tests.components.Comp"
              provides="zope.component.tests.components.IApp"
              for="zope.component.tests.components.IContent"
              name="test"
              />
            """
            )))

        self.assertEqual(
            zapi.getAdapter(Content(), IApp, "test").__class__, Comp)

    def testProtectedAdapter(self):

        # Full import is critical!
        from zope.component.tests.components import Content, IApp, Comp

        self.assertEqual(IV(Content(), None), None)

        xmlconfig(StringIO(template % (
            """
            <adapter
              factory="zope.component.tests.components.Comp"
              provides="zope.component.tests.components.IApp"
              for="zope.component.tests.components.IContent"
              permission="zope.Public"
              />
            """
            )))

        adapter = ProxyFactory(IApp(Content()))
        items = [item[0] for item in getTestProxyItems(adapter)]
        self.assertEqual(items, ['a', 'f'])
        self.assertEqual(removeSecurityProxy(adapter).__class__, Comp)

    def testAdapterUndefinedPermission(self):
        config = StringIO(template % (
             """
             <adapter
              factory="zope.component.tests.components.Comp"
              provides="zope.component.tests.components.IApp"
              for="zope.component.tests.components.IContent"
              permission="zope.UndefinedPermission"
              />
            """
            ))
        self.assertRaises(ValueError, xmlconfig, config, testing=1)

    def testUtility(self):

        # Full import is critical!
        from zope.component.tests.components import IApp, comp

        self.assertEqual(zapi.queryUtility(IV), None)

        xmlconfig(StringIO(template % (
            """
            <utility
              component="zope.component.tests.components.comp"
              provides="zope.component.tests.components.IApp"
              />
            """
            )))

        self.assertEqual(zapi.getUtility(IApp), comp)

    def testNamedUtility(self):

        # Full import is critical!
        from zope.component.tests.components import IApp, comp

        self.testUtility()

        self.assertEqual(zapi.queryUtility(IV, 'test'), None)

        xmlconfig(StringIO(template % (
            """
            <utility
              component="zope.component.tests.components.comp"
              provides="zope.component.tests.components.IApp"
              name="test"
              />
            """
            )))

        self.assertEqual(zapi.getUtility(IApp, "test"), comp)

    def testUtilityFactory(self):

        # Full import is critical!
        from zope.component.tests.components import IApp, Comp

        self.assertEqual(zapi.queryUtility(IV), None)

        xmlconfig(StringIO(template % (
            """
            <utility
              factory="zope.component.tests.components.Comp"
              provides="zope.component.tests.components.IApp"
              />
            """
            )))

        self.assertEqual(zapi.getUtility(IApp).__class__, Comp)

    def testProtectedUtility(self):

        # Full import is critical!
        from zope.component.tests.components import IApp, comp

        self.assertEqual(zapi.queryUtility(IV), None)

        xmlconfig(StringIO(template % (
            """
            <utility
              component="zope.component.tests.components.comp"
              provides="zope.component.tests.components.IApp"
              permission="zope.Public"
              />
            """
            )))

        utility = ProxyFactory(zapi.getUtility(IApp))
        items = [item[0] for item in getTestProxyItems(utility)]
        self.assertEqual(items, ['a', 'f'])
        self.assertEqual(removeSecurityProxy(utility), comp)

    def testUtilityUndefinedPermission(self):
        config = StringIO(template % (
             """
             <utility
              component="zope.component.tests.components.comp"
              provides="zope.component.tests.components.IApp"
              permission="zope.UndefinedPermission"
              />
            """
            ))
        self.assertRaises(ValueError, xmlconfig, config,
                          testing=1)


    def testView(self):
        ob = Ob()
        self.assertEqual(zapi.queryView(ob, 'test', Request(IV), None), None)

        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="zope.app.component.tests.views.V1"
                  for="zope.app.component.tests.views.IC"
                  type="zope.app.component.tests.views.IV"/>
            """
            ))

        self.assertEqual(
            zapi.queryView(ob, 'test', Request(IV), None).__class__,
            V1)


    def testMultiView(self):
        from zope.app.component.tests.adapter import A1, A2, A3, I3
        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="zope.app.component.tests.adapter.A3"
                  for="zope.app.component.tests.views.IC
                       zope.app.component.tests.adapter.I1
                       zope.app.component.tests.adapter.I2
                       "
                  type="zope.app.component.tests.views.IV"/>
            """
            ))


        ob = Ob()
        a1 = A1()
        a2 = A2()
        request = Request(IV)
        view = zapi.queryMultiView((ob, a1, a2), request, name='test')
        self.assertEqual(view.__class__, A3)
        self.assertEqual(view.context, (ob, a1, a2, request))

    def testMultiView_fails_w_multiple_factories(self):
        from zope.app.component.tests.adapter import A1, A2, A3, I3
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(template %
              """
              <view name="test"
                    factory="zope.app.component.tests.adapter.A3
                             zope.app.component.tests.adapter.A2"
                    for="zope.app.component.tests.views.IC
                         zope.app.component.tests.adapter.I1
                         zope.app.component.tests.adapter.I2
                         "
                    type="zope.app.component.tests.views.IV"/>
              """
              )
            )

    def testView_w_multiple_factories(self):
        from zope.app.component.tests.adapter import A1, A2, A3

        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="zope.app.component.tests.adapter.A1
                           zope.app.component.tests.adapter.A2
                           zope.app.component.tests.adapter.A3
                           zope.app.component.tests.views.V1"
                  for="zope.app.component.tests.views.IC"
                  type="zope.app.component.tests.views.IV"/>
            """
            ))

        ob = Ob()

        # The view should be a V1 around an A3, around an A2, around
        # an A1, anround ob:
        view = zapi.queryView(ob, 'test', Request(IV))
        self.assertEqual(view.__class__, V1)
        a3 = view.context
        self.assertEqual(a3.__class__, A3)
        a2 = a3.context[0]
        self.assertEqual(a2.__class__, A2)
        a1 = a2.context[0]
        self.assertEqual(a1.__class__, A1)
        self.assertEqual(a1.context[0], ob)

    def testView_fails_w_no_factories(self):
        from zope.app.component.tests.adapter import A1, A2, A3

        self.assertRaises(ConfigurationError,
                          xmlconfig,
                          StringIO(template %
                                   """
                                   <view name="test"
                                   factory=""
                                   for="zope.app.component.tests.views.IC"
                                   type="zope.app.component.tests.views.IV"/>
                                   """
                                   ),
                          )

        
    def testViewThatProvidesAnInterface(self):

        ob = Ob()
        self.assertEqual(zapi.queryView(ob, 'test', Request(IV), None), None)

        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="zope.app.component.tests.views.V1"
                  for="zope.app.component.tests.views.IC"
                  type="zope.app.component.tests.views.IR"
                  />
            """
            ))

        v = zapi.queryView(ob, 'test', Request(IR), None, providing=IV)
        self.assertEqual(v, None)

        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="zope.app.component.tests.views.V1"
                  for="zope.app.component.tests.views.IC"
                  type="zope.app.component.tests.views.IR"
                  provides="zope.app.component.tests.views.IV"
                  />
            """
            ))

        v = zapi.queryView(ob, 'test', Request(IR), None, providing=IV)

        self.assertEqual(v.__class__,
                         V1)

    def testUnnamedViewThatProvidesAnInterface(self):

        ob = Ob()
        self.assertEqual(zapi.queryView(ob, '', Request(IV), None), None)

        xmlconfig(StringIO(template %
            """
            <view factory="zope.app.component.tests.views.V1"
                  for="zope.app.component.tests.views.IC"
                  type="zope.app.component.tests.views.IR"
                  />
            """
            ))

        v = zapi.queryView(ob, '', Request(IR), None, providing=IV)
        self.assertEqual(v, None)

        xmlconfig(StringIO(template %
            """
            <view factory="zope.app.component.tests.views.V1"
                  for="zope.app.component.tests.views.IC"
                  type="zope.app.component.tests.views.IR"
                  provides="zope.app.component.tests.views.IV"
                  />
            """
            ))

        v = zapi.queryView(ob, '', Request(IR), None, providing=IV)

        self.assertEqual(v.__class__, V1)

    def testInterfaceProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="zope.app.component.tests.views.V1"
                  for="zope.app.component.tests.views.IC"
                  type="zope.app.component.tests.views.IV"
                  permission="zope.Public"
              allowed_interface="zope.app.component.tests.views.IV"
                  />
            """
            ))

        v = ProxyFactory(zapi.getView(Ob(), 'test', Request(IV)))
        self.assertEqual(v.index(), 'V1 here')
        self.assertRaises(Exception, getattr, v, 'action')

    def testAttributeProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="zope.app.component.tests.views.V1"
                  for="zope.app.component.tests.views.IC"
                  type="zope.app.component.tests.views.IV"
                  permission="zope.Public"
                  allowed_attributes="action"
                  />
            """
            ))

        v = ProxyFactory(zapi.getView(Ob(), 'test', Request(IV)))
        self.assertEqual(v.action(), 'done')
        self.assertRaises(Exception, getattr, v, 'index')

    def testInterfaceAndAttributeProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="zope.app.component.tests.views.V1"
                  for="zope.app.component.tests.views.IC"
                  type="zope.app.component.tests.views.IV"
                  permission="zope.Public"
                  allowed_attributes="action"
              allowed_interface="zope.app.component.tests.views.IV"
                  />
            """
            ))

        v = zapi.getView(Ob(), 'test', Request(IV))
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testDuplicatedInterfaceAndAttributeProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="zope.app.component.tests.views.V1"
                  for="zope.app.component.tests.views.IC"
                  type="zope.app.component.tests.views.IV"
                  permission="zope.Public"
                  allowed_attributes="action index"
              allowed_interface="zope.app.component.tests.views.IV"
                  />
            """
            ))

        v = zapi.getView(Ob(), 'test', Request(IV))
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testIncompleteProtectedViewNoPermission(self):
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(template %
            """
            <view name="test"
                  factory="zope.app.component.tests.views.V1"
                  for="zope.app.component.tests.views.IC"
                  type="zope.app.component.tests.views.IV"
                  allowed_attributes="action index"
                  />
            """
            ))

    def testViewUndefinedPermission(self):
        config = StringIO(template % (
            """
            <view name="test"
                  factory="zope.app.component.tests.views.V1"
                  for="zope.app.component.tests.views.IC"
                  type="zope.app.component.tests.views.IV"
                  permission="zope.UndefinedPermission"
                  allowed_attributes="action index"
              allowed_interface="zope.app.component.tests.views.IV"
                  />
            """
            ))
        self.assertRaises(ValueError, xmlconfig, config, testing=1)


    def testDefaultView(self):

        ob = Ob()
        self.assertEqual(zapi.queryView(ob, 'test', Request(IV), None), None)

        xmlconfig(StringIO(template % (
            """
            <defaultView name="test"
                  for="zope.app.component.tests.views.IC"
                  type="zope.app.component.tests.views.IV"/>
            """
            )))

        self.assertEqual(zapi.queryView(ob, 'test', Request(IV), None), None)
        self.assertEqual(zapi.getDefaultViewName(ob, Request(IV)), 'test')

    def testResource(self):

        ob = Ob()
        self.assertEqual(
            zapi.queryResource('test', Request(IV), None), None)
        xmlconfig(StringIO(template % (
            """
            <resource name="test"
                  factory="zope.app.component.tests.views.R1"
                  type="zope.app.component.tests.views.IV"/>
            """
            )))

        self.assertEqual(
            zapi.queryResource('test', Request(IV), None).__class__,
            R1)

    def testResourceThatProvidesAnInterface(self):

        ob = Ob()
        self.assertEqual(zapi.queryResource('test', Request(IV), None), None)

        xmlconfig(StringIO(template %
            '''
            <resource
                name="test"
                factory="zope.app.component.tests.views.R1"
                type="zope.app.component.tests.views.IR"
                />
            '''
            ))

        v = zapi.queryResource('test', Request(IR), None, providing=IV)
        self.assertEqual(v, None)

        xmlconfig(StringIO(template %
            '''
            <resource
                name="test"
                factory="zope.app.component.tests.views.R1"
                type="zope.app.component.tests.views.IR"
                provides="zope.app.component.tests.views.IV"
                />
            '''
            ))

        v = zapi.queryResource('test', Request(IR), None, providing=IV)

        self.assertEqual(v.__class__, R1)

    def testUnnamedResourceThatProvidesAnInterface(self):

        ob = Ob()
        self.assertEqual(zapi.queryResource('', Request(IV), None), None)

        xmlconfig(StringIO(template %
            '''
            <resource
                factory="zope.app.component.tests.views.R1"
                type="zope.app.component.tests.views.IR"
                />
            '''
            ))

        v = zapi.queryResource('', Request(IR), None, providing=IV)
        self.assertEqual(v, None)

        xmlconfig(StringIO(template %
            '''
            <resource
                factory="zope.app.component.tests.views.R1"
                type="zope.app.component.tests.views.IR"
                provides="zope.app.component.tests.views.IV"
                />
            '''
            ))

        v = zapi.queryResource('', Request(IR), None, providing=IV)

        self.assertEqual(v.__class__, R1)

    def testResourceUndefinedPermission(self):

        config = StringIO(template % (
            '''
            <resource name="test"
                  factory="zope.app.component.tests.views.R1"
                  type="zope.app.component.tests.views.IV"
                  permission="zope.UndefinedPermission"/>
            '''
            ))
        self.assertRaises(ValueError, xmlconfig, config, testing=1)

    def testFactory(self):

        self.assertRaises(ComponentLookupError, zapi.createObject, None, 'foo')

        xmlconfig(StringIO(template % (
            '''
            <factory
               id="foo.bar"
               component="zope.app.component.tests.factory.f"
               />
            '''
            )))

        from factory import X
        self.assertEqual(zapi.createObject(None, 'foo.bar').__class__, X)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        DocTestSuite(),
        ))

if __name__ == "__main__":
    unittest.TextTestRunner().run(test_suite())
