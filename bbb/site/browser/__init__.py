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
"""View support for adding and configuring services and other components.

$Id$
"""
from zope.security.proxy import removeSecurityProxy
from zope.app import zapi
from zope.app.container.browser.adding import Adding
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.container.interfaces import INameChooser
from zope.app.registration.interfaces import UnregisteredStatus
from zope.app.registration.interfaces import RegisteredStatus
from zope.app.registration.interfaces import ActiveStatus
from zope.app.component.bbb.site.interfaces import ILocalService
from zope.app.utility.interfaces import ILocalUtility
from zope.app.site.service import ServiceRegistration
from zope.app.publisher.browser import BrowserView
from zope.app.site.interfaces import ISite, ISiteManager
from zope.app.site.service import SiteManager
from zope.app.component.localservice import getNextServices
from zope.component.service import IGlobalServiceManager
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
            url = zapi.absoluteURL(self.added_object, self.request)
            return url + "/@@registration.html"

        return super(ComponentAdding, self).nextURL()

    def action(self, type_name, id=''):
        # For special case of that we want to redirect to another adding view
        # (usually another menu such as AddService)
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


class ServiceAdding(ComponentAdding):
    """Adding subclass used for adding services."""

    menu_id = None
    title = _("Add Service")

    _addFilterInterface = ILocalService

    def add(self, content):
        # Override so as to check the type of the new object.
        if not ILocalService.providedBy(content):
            raise TypeError("%s is not a local service" % content)

        content = super(ServiceAdding, self).add(content)

        # figure out the interfaces that this service implements
        sm = zapi.getServices()
        implements = []
        for type_name, interface in sm.getServiceDefinitions():
            if interface.providedBy(content):
                implements.append(type_name)

        rm = content.__parent__.getRegistrationManager()
        chooser = INameChooser(rm)

        # register an activated service registration
        for type_name in implements:
            sc = ServiceRegistration(type_name, content, content)
            name = chooser.chooseName(type_name, sc)
            rm[name] = sc
            sc.status = ActiveStatus

        return content


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
            url = zapi.absoluteURL(self.added_object, self.request)
            return url + "/addRegistration.html"

        return super(UtilityAdding, self).nextURL()


class AddServiceRegistration(BrowserView):
    """A view on a service implementation, used by add_svc_config.pt."""

    def listServiceTypes(self):

        # Collect all defined services interfaces that it implements.
        sm = zapi.getServices()
        lst = []
        for servicename, interface in sm.getServiceDefinitions():
            if interface.providedBy(self.context):
                registry = sm.queryRegistrations(servicename)
                checked = True
                if registry and registry.active():
                    checked = False
                d = {'name': servicename, 'checked': checked}
                lst.append(d)
        return lst

    def action(self, name=[], active=[]):
        rm = self.context.__parent__.getRegistrationManager()
        chooser = INameChooser(rm)

        for nm in name:
            sc = ServiceRegistration(nm, self.context, self.context)
            name = chooser.chooseName(nm, sc)
            rm[name] = sc
            if nm in active:
                sc.status = ActiveStatus
            else:
                sc.status = RegisteredStatus

        self.request.response.redirect("@@SelectedManagementView.html")


class ServiceSummary(BrowserView):
    """A view on the service manager, used by services.pt."""

    def update(self):
        """Possibly delete one or more services.

        In that case, issue a message.
        """
        todo = self.request.get("selected")
        doActivate = self.request.get("Activate")
        doDeactivate = self.request.get("Deactivate")
        doDelete = self.request.get("Delete")
        if not todo:
            if doActivate or doDeactivate or doDelete:
                return _("Please select at least one checkbox")
            return None
        if doActivate:
            return self._activate(todo)
        if doDeactivate:
            return self._deactivate(todo)
        if doDelete:
            return self._delete(todo)

    def _activate(self, todo):
        done = []
        for name in todo:
            registry = self.context.queryRegistrations(name)
            obj = registry.active()
            if obj is None:
                # Activate the first registered registration
                obj = registry.info()[0]['registration']
                obj.status = ActiveStatus
                done.append(name)
        if done:
            s = _("Activated: ${activated_services}")
            s.mapping = {'activated_services': ", ".join(done)}
            return s
        else:
            return _("All of the checked services were already active")

    def _deactivate(self, todo):
        done = []
        for name in todo:
            registry = self.context.queryRegistrations(name)
            obj = registry.active()
            if obj is not None:
                obj.status = RegisteredStatus
                done.append(name)
        if done:
            s = _("Deactivated: ${deactivated_services}")
            s.mapping = {'deactivated_services': ", ".join(done)}
            return s
        else:
            return _("None of the checked services were active")

    def _delete(self, todo):
        errors = []
        for name in todo:
            registry = self.context.queryRegistrations(name)
            assert registry
            if registry.active() is not None:
                errors.append(name)
                continue
        if errors:
            s = _("Can't delete active service(s): ${service_names}; "
                  "use the Deactivate button to deactivate")
            s.mapping = {'service_names': ", ".join(errors)}
            return s

        # 1) Delete the registrations
        services = {}
        for name in todo:
            registry = self.context.queryRegistrations(name)
            assert registry
            assert registry.active() is None # Phase error
            for info in registry.info():
                conf = info['registration']
                obj = conf.component
                path = zapi.getPath(obj)
                services[path] = obj
                conf.status = UnregisteredStatus
                parent = zapi.getParent(conf)
                name = zapi.name(conf)
                del parent[name]

        # 2) Delete the service objects
        # XXX Jim doesn't like this very much; he thinks it's too much
        #     magic behind the user's back.  OTOH, Guido believes that
        #     we're providing an abstraction here that hides the
        #     existence of the folder and its registration manager as
        #     much as possible, so it's appropriate to clean up when
        #     deleting a service; if you don't want that, you can
        #     manipulate the folder explicitly.
        for path, obj in services.items():
            parent = zapi.getParent(obj)
            name = zapi.name(obj)
            del parent[name]

        s = _("Deleted: ${service_names}")
        s.mapping = {'service_names': ", ".join(todo)}
        return s

    def listConfiguredServices(self):
        return gatherConfiguredServices(self.context, self.request)

def gatherConfiguredServices(sm, request, items=None):
    """Find all s/service/site managers up to the root and gather info
    about their services.
    """
    if items is None:
        items = {}
        # make sure no-one tries to use this starting at the global service
        # manager
        assert ISiteManager.providedBy(sm)
        manageable = True
    else:
        # don't want the "change registration" link for parent services
        manageable = False

    if IGlobalServiceManager.providedBy(sm):
        # global service manager
        names = []
        for type_name, interface in sm.getServiceDefinitions():
            if items.has_key(type_name):
                # a child has already supplied one of these
                continue
            try:
                sm.getService(type_name)
            except ComponentLookupError:
                pass
            else:
                names.append(type_name)
                items[type_name] = {'name': type_name, 'url': '',
                    'parent': _('global'), 'disabled': False,
                    'manageable': False}
        return

    for name in sm.listRegistrationNames():
        if items.has_key(name):
            # a child has already supplied one of these
            continue

        registry = sm.queryRegistrations(name)
        assert registry
        infos = [info for info in registry.info() if info['active']]
        if infos:
            configobj = infos[0]['registration']
            component = configobj.component
            url = str(
                zapi.getView(component, 'absolute_url', request))
        else:
            url = ""
        items[name] = {'name': name, 'url': url, 'parent': 'parent',
            'disabled': not url, 'manageable': manageable}

    # look for more
    gatherConfiguredServices(getNextServices(sm), request, items)

    # make it a list and sort by name
    items = items.values()
    items.sort(lambda a,b:cmp(a['name'], b['name']))
    return items

class ServiceActivation(BrowserView):
    """A view on the service manager, used by serviceactivation.pt.

    This really wants to be a view on a registration registry
    containing service registrations, but registries don't have names,
    so we make it a view on the service manager; the request parameter
    'type' determines which service is to be configured."""

    def isDisabled(self):
        sm = zapi.getServices()
        registry = sm.queryRegistrations(self.request.get('type'))
        return not (registry and registry.active())

    def listRegistry(self):
        sm = zapi.getServices()
        registry = sm.queryRegistrations(self.request.get('type'))
        if not registry:
            return []

        # XXX this code path is not being tested
        result = []
        for info in registry.info():
            configobj = info['registration']
            component = configobj.component
            path = zapi.getPath(component)
            path = path.split("/")
            info['id'] = zapi.getPath(configobj)
            info['name'] = "/".join(path[-2:])
            info['url'] = str(
                zapi.getView(component, 'absolute_url', self.request))
            info['config'] = str(zapi.getView(configobj, 'absolute_url',
                                         self.request))
            result.append(info)

        result.append({'id': 'None',
                       'active': False,
                       'registration': None,
                       'name': '',
                       'url': '',
                       'config': '',
                       })
        return result

    def update(self):
        active = self.request.get("active")
        if not active:
            return ""

        sm = zapi.getServices()
        registry = sm.queryRegistrations(self.request.get('type'))
        if not registry:
            return _("Invalid service type specified")
        old_active = registry.active()
        if active == "None":
            new_active = None
        else:
            new_active = zapi.traverse(sm, active)
        if old_active == new_active:
            return _("No change")

        if new_active is None:
            registry.activate(None)
            return _("Service deactivated")
        else:
            new_active.status = ActiveStatus
            s = _("${active_services} activated")
            s.mapping = {'active_services': active}
            return s

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
        sm = SiteManager(bare)
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

    def getServices(self):
        """Return an iterable of service dicts

        where the service dicts contains keys "name" and "registrations."
        registrations is a list of IRegistrations.
        """
        sm = zapi.getServices()
        for name, iface in sm.getServiceDefinitions():
            try:
                service = sm.getService(name)
            except ComponentLookupError:
                pass
            else:
                registry = IInterfaceBasedRegistry(service, None)
                if registry is not None:
                    regs = list(registry.getRegistrationsForInterface(
                        self.iface))
                    if regs:
                        yield {"name": name, "registrations": regs}
            

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

