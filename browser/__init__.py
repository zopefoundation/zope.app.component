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
"""View support for adding and configuring utilities and adapters.

$Id$
"""
from zope.component.interfaces import ISiteManager
from zope.security.proxy import removeSecurityProxy
from zope.app import zapi
from zope.app.container.browser.adding import Adding
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.container.interfaces import INameChooser
from zope.app.component.interfaces.registration import ActiveStatus
from zope.app.component.interfaces.registration import InactiveStatus
from zope.app.component.interfaces import ILocalUtility
from zope.app.publisher.browser import BrowserView
from zope.app.component.interfaces import ISite
from zope.app.component.site import LocalSiteManager
from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IFactory
from zope.interface.interfaces import IMethod
from zope.schema.interfaces import IField
from zope.app.interface.interfaces import IInterfaceBasedRegistry
from zope.app.component.interface import searchInterface
from zope.app.component.interface import getInterface
from zope.app.component.interface import provideInterface

class ComponentAdding(Adding):
    """Adding subclass used for registerable components."""

    menu_id = "add_component"

    def add(self, content):
        # Override so as to save a reference to the added object
        self.added_object = super(ComponentAdding, self).add(content)
        return self.added_object

    def nextURL(self):
        v = zapi.queryView(
            self.added_object, "registration.html", self.request)
        if v is not None:
            url = str(
                zapi.getView(self.added_object, 'absolute_url', self.request))
            return url + "/@@registration.html"

        return super(ComponentAdding, self).nextURL()

    def action(self, type_name, id=''):
        # For special case of that we want to redirect to another adding view
        # (usually another menu such as AddUtility)
        if type_name.startswith("../"):
            # Special case
            url = type_name
            if id:
                url += "?id=" + id
            self.request.response.redirect(url)
            return

        # Call the superclass action() method.
        # As a side effect, self.added_object is set by add() above.
        super(ComponentAdding, self).action(type_name, id)

    _addFilterInterface = None

    def addingInfo(self):
        # A site management folder can have many things. We only want 
        # things that implement a particular interface
        info = super(ComponentAdding, self).addingInfo()
        if self._addFilterInterface is None:
            return info
        out = []
        for item in info:
            extra = item.get('extra')
            if extra:
                factoryname = extra.get('factory')
                if factoryname:
                    factory = zapi.getUtility(IFactory, factoryname)
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

    _addFilterInterface = ILocalUtility

    def add(self, content):
        # Override so as to check the type of the new object.
        if not ILocalUtility.providedBy(content):
            raise TypeError("%s is not a local utility" % content)
        return super(UtilityAdding, self).add(content)

    def nextURL(self):
        v = zapi.queryView(
            self.added_object, "addRegistration.html", self.request)
        if v is not None:
            url = str(
                zapi.getView(self.added_object, 'absolute_url', self.request))
            return url + "/addRegistration.html"

        return super(UtilityAdding, self).nextURL()


class MakeSite(BrowserView):
    """View for converting a possible site to a site."""

    def addSiteManager(self):
        """Convert a possible site to a site

        >>> from zope.app.traversing.interfaces import IContainmentRoot
        >>> from zope.interface import implements

        >>> class PossibleSite(object):
        ...     implements(IContainmentRoot)
        ...     def setSiteManager(self, sm):
        ...         from zope.interface import directlyProvides
        ...         directlyProvides(self, ISite)


        >>> folder = PossibleSite()

        >>> from zope.publisher.browser import TestRequest
        >>> request = TestRequest()

        Now we'll make our folder a site:

        >>> MakeSite(folder, request).addSiteManager()

        Now verify that we have a site:

        >>> ISite.providedBy(folder)
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
        UserError: This is already a site

        """
        if ISite.providedBy(self.context):
            raise zapi.UserError('This is already a site')

        # We don't want to store security proxies (we can't,
        # actually), so we have to remove proxies here before passing
        # the context to the SiteManager.
        bare = removeSecurityProxy(self.context)
        sm = LocalSiteManager(bare)
        self.context.setSiteManager(sm)
        self.request.response.redirect(
            "++etc++site/@@SelectedManagementView.html")


class Interfaces(object):
    """Interface service view

    >>> from zope.interface import Interface
    >>> from zope.app.content.interfaces import IContentType
    >>> class DCInterface(Interface):
    ...     '''DCInterfaceDoc
    ...
    ...     This is a multi-line doc string.
    ...     '''
    ... 
    >>> class DummyInterface(object):
    ...     def items(self):
    ...         return [('DCInterface', DCInterface)]
    ...
    >>> provideInterface('', DCInterface, IContentType)
    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> interface_view = Interfaces(DummyInterface(), request)
    >>> from pprint import PrettyPrinter
    >>> pprint=PrettyPrinter(width=50).pprint
    >>> pprint(interface_view.getInterfaces())
    [{'doc': 'DCInterfaceDoc',
      'id': 'zope.app.site.browser.DCInterface',
      'name': 'DCInterface'}]
        

    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getInterfaces(self):
        L = [(iface.__name__, iface.__module__+'.'+iface.__name__,
              getattr(iface, '__doc__', '').split('\n')[0].strip()
              )
             for iface in searchInterface(self.context)]
        L.sort()
        return [{"id": id, "name": name, "doc": doc} for name, id, doc in L]

class Detail(object):
    """Interface Details

    >>> from zope.schema import TextLine
    >>> from zope.interface import Interface
    >>> from zope.app.content.interfaces import IContentType
    >>> from zope.i18n import MessageIDFactory
    >>> from zope.interface.interfaces import IInterface
    >>> _ = MessageIDFactory('zope')
    >>> class TestInterface(Interface):
    ...     '''Test Interface'''
    ...     test_field = TextLine(title = _(u'Test Name'))
    ...     def testMethod():
    ...         'Returns test name'
    ...
    >>> class TestClass(object):
    ...     def getInterface(self, id=None):
    ...         return TestInterface
    ...
    >>> IInterface.providedBy(TestInterface)
    True
    >>> provideInterface('', TestInterface, IContentType)
    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> form = {'id': 'zope.app.site.browser.TestInterface'}
    >>> request.form = form
    >>> interface_details = Detail(TestClass(), request)
    >>> interface_details.setup()
    >>> interface_details.name
    'TestInterface'
    >>> interface_details.doc
    'Test Interface'
    >>> interface_details.iface.__name__
    'TestInterface'
    >>> [method['method'].__name__ for method in
    ...     interface_details.methods]
    ['testMethod']
    >>> [field.__name__ for field in interface_details.schema]
    ['test_field']
    
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def setup(self):
        try:
            id = self.request["id"]
        except KeyError:
            raise zapi.UserError("Please click on an interface name to view"
                  " details.")
        
        iface = getInterface(self.context, id)

        from zope.proxy import getProxiedObject
        self.iface = getProxiedObject(iface)
        
        self.name = self.iface.__name__
        self.doc = getattr(self.iface, '__doc__', '')
        self.methods = []
        self.schema = []

        for name in self.iface:
            defn = self.iface[name]
            if IMethod.providedBy(defn):
                title = defn.__doc__.split('\n')[0].strip()
                self.methods.append({'method': defn, 'title': title})
            elif IField.providedBy(defn):
                self.schema.append(defn)

class MethodDetail(object):
    """Interface Method Details

    >>> from zope.interface import Interface
    >>> from zope.i18n import MessageIDFactory
    >>> _ = MessageIDFactory('zope')
    >>> class TestInterface(Interface):
    ...     '''Test Interface'''
    ...     def testMethod():
    ...         'Returns test name'
    ...
    >>> class TestClass(object):
    ...     def getInterface(self, id=None):
    ...         return TestInterface
    ...
    >>> provideInterface('', TestInterface)
    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> form = {
    ... 'interface_id': 'zope.app.site.browser.TestInterface',
    ... 'method_id': 'testMethod'}
    >>> request.form = form
    >>> imethod_details = MethodDetail(TestClass(), request)
    >>> imethod_details.setup()
    >>> imethod_details.name
    'testMethod'
    >>> imethod_details.doc
    'Returns test name'
    >>> imethod_details.iface.__name__
    'TestInterface'
    >>> imethod_details.method.__name__
    'testMethod'

    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def setup(self):
        try:
            interface_id = self.request["interface_id"]
        except KeyError:
            raise zapi.UserError("Please click on a method name in the Detail"
                                 " tab to view method details.")
        try:
            method_id = self.request["method_id"]
        except KeyError:
            raise zapi.UserError("Please click on a method name to view"
                  " details.")
        
        iface = getInterface(self.context, interface_id)

        from zope.proxy import getProxiedObject
        self.iface = getProxiedObject(iface)

        self.method = self.iface[method_id]
        self.name = self.method.__name__
        self.doc = self.method.__doc__

