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
"""Use-Registration view for utilities.

$Id$
"""
from zope.interface import providedBy
from zope.security.proxy import removeSecurityProxy

from zope.app import zapi
from zope.app.component.browser.registration import AddComponentRegistration
from zope.app.component.interfaces.registration import ActiveStatus
from zope.app.introspector import interfaceToName

from zope.app.i18n import ZopeMessageIDFactory as _


class AddRegistration(AddComponentRegistration):
    """View for adding a utility registration.

    We could just use AddComponentRegistration, except that we need a
    custom interface widget.

    This is a view on a local utility, configured by an <addform>
    directive.
    """
    def add(self, registration):
        reg = super(AddRegistration, self).add(registration)
        reg.status = ActiveStatus
        return reg


class Utilities(object):
    # self.context is the local utility service

    def update(self):
        """Possibly delete one or more utilities.

        In that case, issue a message.
        """
        selected = self.request.get("selected")
        doActivate = self.request.get("Activate")
        doDeactivate = self.request.get("Deactivate")
        doDelete = self.request.get("Delete")
        if not selected:
            if doActivate or doDeactivate or doDelete:
                return _("Please select at least one checkbox")
            return None
        folder = zapi.getParent(self.context)
        todo = []
        for key in selected:
            name, ifacename = key.split(":", 1)
            iface = folder.resolve(ifacename)
            todo.append((key, name, iface))
        if doActivate:
            return self._activate(todo)
        if doDeactivate:
            return self._deactivate(todo)
        if doDelete:
            return self._delete(todo)

    def _activate(self, todo):
        done = []
        for key, name, iface in todo:
            registry = self.context.queryRegistrations(name, iface)
            obj = registry.active()
            if obj is None:
                # Activate the first registered registration
                obj = registry.info()[0]['registration']
                obj.status = ActiveStatus
                done.append(obj.usageSummary())
        if done:
            s = _("Activated: ${activated_utilities}")
            s.mapping = {'activated_utilities': ", ".join(done)}
            return s
        else:
            return _("All of the checked utilities were already active")

    def _deactivate(self, todo):
        done = []
        for key, name, iface in todo:
            registry = self.context.queryRegistrations(name, iface)
            obj = registry.active()
            if obj is not None:
                obj.status = RegisteredStatus
                done.append(obj.usageSummary())
        if done:
            s = _("Deactivated: ${deactivated_utilities}")
            s.mapping = {'deactivated_utilities': ", ".join(done)}
            return s
        else:
            return _("None of the checked utilities were active")

    def _delete(self, todo):
        errors = []
        for key, name, iface in todo:
            registry = self.context.queryRegistrations(name, iface)
            assert registry
            obj = registry.active()
            if obj is not None:
                errors.append(obj.usageSummary())
                continue
        if errors:
            s = _("Can't delete active utility/utilites: ${utility_names}; "
                  "use the Deactivate button to deactivate")
            s.mapping = {'utility_names': ", ".join(errors)}
            return s

        # 1) Delete the registrations
        services = {}
        done = []
        for key, name, iface in todo:
            registry = self.context.queryRegistrations(name, iface)
            assert registry
            assert registry.active() is None # Phase error
            first = True
            for info in registry.info():
                conf = info['registration']
                obj = conf.component
                done.append(conf.usageSummary())
                path = zapi.getPath(obj)
                services[path] = obj
                conf.status = UnregisteredStatus
                parent = zapi.getParent(conf)
                name = zapi.getName(conf)
                del parent[name]

        # 2) Delete the service objects
        for path, obj in services.items():
            parent = zapi.getParent(obj)
            name = zapi.getName(obj)
            del parent[name]
            
        s = _("Deleted: ${utility_names}")
        s.mapping = {'utility_names': ", ".join(done)}
        return s

    def getConfigs(self):
        utils = self.context
        L = []
        for registration in utils.registrations(localOnly=True):
            ifname = interfaceToName(self.context, registration.provided)
            d = {"interface": ifname,
                 "name": registration.name,
                 "url": "",
                 "summary": registration.usageSummary(),
                 "configurl": ("@@configureutility.html?interface=%s&name=%s"
                               % (ifname, registration.name)),
                 }
            stack = utils.queryRegistrationsFor(registration)
            if stack.active():
                d["url"] = str(zapi.getView(registration.component,
                                            "absolute_url", self.request))
            L.append((ifname, registration.name, d))
        L.sort()
        return [d for ifname, name, d in L]


class ConfigureUtility(object):
    def update(self):
        folder = zapi.getParent(self.context)
        iface = folder.resolve(self.request['interface'])
        name = self.request['name']
        iface = removeSecurityProxy(iface)
        regstack = self.context.queryRegistrations(name, iface)
        form = zapi.getView(regstack, "ChangeRegistrations", self.request)
        form.update()
        return form
