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
"""Tools View

$Id$
"""
from zope.interface import implements, Attribute
from zope.interface.interfaces import IInterface
from zope.app.pagetemplate.simpleviewclass import simple as SimpleView
from zope.app.publisher.interfaces.browser import IBrowserView
from zope.app import zapi
from zope.app.copypastemove import rename
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.servicenames import Services, Utilities
from zope.app.utility.browser import AddRegistration
from zope.app.utility import UtilityRegistration
from zope.app.site.browser import ComponentAdding
from zope.app.site.folder import SiteManagementFolder
from zope.app.registration.interfaces import UnregisteredStatus
from zope.app.registration.interfaces import RegisteredStatus
from zope.app.registration.interfaces import ActiveStatus
from zope.app.site.browser import ServiceAdding

from zope.app.i18n import ZopeMessageIDFactory as _


class IToolType(IInterface):
    """Interfaces implementing the tool type are considered tools."""

class IToolView(IBrowserView):

    title = Attribute("Title for the view.")
    description = Attribute("Description for the view.")

    def update(self):
        """Update the data."""

    def getComponents(self):
        """Return a list of components."""


class IUtilityToolView(IToolView):

    interface = Attribute("Interface the utility provides.")


class ToolsOverview(object):
    def getTools(self):
        tools = []
        for n, iface in zapi.getUtilitiesFor(IToolType):
            name = iface.getName()
            view = zapi.getView(self.context, 'manage%sTool.html' % name,
                                self.request)
            tools.append({'title':view.title,
                          'description':view.description,
                          'action':'./@@manage%sTool.html' % name })
        tools.sort(lambda x, y: cmp(x['title'], y['title']))
        return tools

class ToolsBacklink(object):
    def getLink(self):
        service = zapi.getService(Services)
        iface = zapi.queryType(self.context, IToolType)
        url = '%s/manage%sTool.html' %(zapi.getPath(service), iface.getName())

        return self.request.response.redirect(url)

class AbstractToolView(SimpleView):
    """Abstract tools view."""

    index = ViewPageTemplateFile('tool.pt')

    title = None
    description = None

    can_rename = False

    def update(self):
        status = ''
        self.renameList = []

        has_key = self.request.form.has_key
        selected = self.request.form.get('selected', [])
        doAdd = has_key('ADD')
        doDelete = has_key('DELETE')
        doRename = has_key('RENAME')
        applyRename = has_key('APPLY_RENAME')
        doActivate = has_key('ACTIVATE')
        doDeactivate = has_key('DEACTIVATE')

        if doAdd:
            self.add()
        elif not selected:
            if (doDelete or doRename or applyRename
                or doActivate or doDeactivate):
                status = _('Please select at least one checkbox')
        elif doDelete:
            self.delete()
            status = _('Deleted selected tools.')
        elif doRename:
            self.renameList = selected
        elif applyRename:
            self.rename()
            status = _('Renamed selected tools.')
        elif doActivate:
            self.activate()
            status = _('Activated registrations.')
        elif doDeactivate:
            self.deactivate()
            status = _('Deactivated registrations.')

        return status

class ServiceToolView(AbstractToolView):
    """Tools view for services."""
    implements(IToolView)

    def delete(self):
        for name in self.request.form['selected']:
            reg = self.context.queryRegistrations(name)

            del_objs = []

            # Delete registrations
            for info in reg.info():
                conf = info['registration']
                obj = conf.component
                conf.status = UnregisteredStatus
                reg_folder = zapi.getParent(conf)
                name = zapi.name(conf)
                del reg_folder[name]
                if obj not in [c.component
                               for c in reg_folder.values()]:
                    del_objs.append(obj)

            # Delete object, if no other registration is available.
            for obj in del_objs:
                parent = zapi.getParent(obj)
                name = zapi.name(obj)
                del parent[name]


    def activate(self):
        for name in self.request.form['selected']:
            reg = self.context.queryRegistrations(name)
            # Activate registrations
            for info in reg.info():
                conf = info['registration']
                conf.status = ActiveStatus

    def deactivate(self):
        for name in self.request.form['selected']:
            reg = self.context.queryRegistrations(name)
            # Deactivate registrations
            for info in reg.info():
                conf = info['registration']
                conf.status = RegisteredStatus

    def add(self):
        self.request.response.redirect('./AddServiceTool')

    def getComponents(self):
        items = []

        for name in self.context.listRegistrationNames():
            registry = self.context.queryRegistrations(name)

            configobj = registry.info()[0]['registration']
            component = configobj.getComponent()
            url = str(
                zapi.getView(component, 'absolute_url', self.request))
            parent = zapi.getParent(component)
            items.append( {'name': name,
                           'url': url,
                           'parent_url': zapi.getPath(parent),
                           'parent_name':zapi.name(parent),
                           'active':registry.info()[0]['active'] })

        return items

class ServiceToolAdding(ServiceAdding):
    """Adding subclass used for adding utilities."""

    title = "Add Service Tool"
    folder = "tools"

    def addingInfo(self):
        if self.folder not in self.context:
            self.context[self.folder] = SiteManagementFolder()
        self.context = self.context[self.folder]
        return super(ServiceToolAdding, self).addingInfo()

    def add(self, content):
        self.context = self.context[self.folder]
        return super(ServiceToolAdding, self).add(content)

    def nextURL(self):
        return '../@@manageILocalServiceTool.html'


class UtilityToolView(AbstractToolView):
    """Tools view for utilities."""

    implements(IUtilityToolView)

    can_rename = True

    def delete(self):
        for name in self.request.form['selected']:
            utils = zapi.getService(Utilities)
            reg = utils.queryRegistrations(name, self.interface)

            del_objs = []

            # Delete registrations
            for info in reg.info():
                conf = info['registration']
                obj = conf.component
                conf.status = UnregisteredStatus
                reg_folder = zapi.getParent(conf)
                name = zapi.name(conf)
                del reg_folder[name]
                if obj not in [c.component
                               for c in reg_folder.values()]:
                    del_objs.append(obj)

            # Delete object, if no other registration is available.
            for obj in del_objs:
                parent = zapi.getParent(obj)
                name = zapi.name(obj)
                del parent[name]

    def rename(self):
        for name in self.request.form['old_names']:
            newname = self.request.form['new_names'][
                self.request.form['old_names'].index(name)]

            utils = zapi.getService('Utilities')
            reg = utils.queryRegistrations(name, self.interface)

            # Rename registrations
            for info in reg.info():
                conf = info['registration']
                orig_status = conf.status
                conf.status = UnregisteredStatus
                conf.name = newname
                conf.status = orig_status

    def activate(self):
        for name in self.request.form['selected']:
            utils = zapi.getService('Utilities')
            reg = utils.queryRegistrations(name, self.interface)

            # Activate registrations
            for info in reg.info():
                conf = info['registration']
                conf.status = ActiveStatus

    def deactivate(self):
        for name in self.request.form['selected']:
            utils = zapi.getService('Utilities')
            reg = utils.queryRegistrations(name, self.interface)

            # Deactivate registrations
            for info in reg.info():
                conf = info['registration']
                conf.status = RegisteredStatus

    def add(self):
        self.request.response.redirect('./Add%sTool' %
                                       self.interface.getName())

    def getComponents(self):
        utils = zapi.getService(Utilities)
        items = []
        for registration in [reg for reg in utils.registrations(localOnly=True)
                             if reg.provided == self.interface]:

            stack = utils.queryRegistrationsFor(registration)
            parent = zapi.getParent(registration.component)
            items.append({
                'name': registration.name,
                'url': zapi.getPath(registration.component),
                'parent_url': zapi.getPath(parent),
                'parent_name': zapi.name(parent),
                'active': stack.active()})

        return items


class UtilityToolAdding(ComponentAdding):
    """Adding subclass used for adding utilities."""

    menu_id = None
    title = "Add Tool"
    folder = "tools"
    _addFilterInterface = None


    def addingInfo(self):
        if self.folder not in self.context:
            self.context[self.folder] = SiteManagementFolder()
        self.context = self.context[self.folder]
        return super(UtilityToolAdding, self).addingInfo()

    def add(self, content):
        if not self._addFilterInterface.providedBy(content):
            raise TypeError("%s is not a %s" %(
                content, self._addFilterInterface.getName()))
        self.context = self.context[self.folder]
        util = super(UtilityToolAdding, self).add(content)

        # Add registration
        registration = UtilityRegistration(self.contentName,
                                           self._addFilterInterface,
                                           util)
        reg_view = AddRegistration(util, self.request)
        reg_view.add(registration)

        return util

    def nextURL(self):
        return '../@@manage%sTool.html' %self._addFilterInterface.getName()
