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
"""Configuration handlers for 'tools' directive.

$Id$
"""
from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserPublisher
from zope.app.component.metaconfigure import view, interface as ifaceDirective
from zope.app.publisher.browser.viewmeta import view as complexView

from zope.app.site.interfaces import ISiteManager
from tools import IToolView, IUtilityToolView, IToolType
from tools import UtilityToolAdding, UtilityToolView
from tools import ServiceToolView, ServiceToolAdding
from zope.app.site.interfaces import ILocalService

def tool(_context, interface, folder="tools", title=None, description=None):
    name = "manage" + interface.getName() + "Tool.html"
    addName = "Add" + interface.getName() + "Tool"
    
    permission = 'zope.ManageContent'

    ifaceDirective(_context, interface, IToolType)

    class_ = type("UtilityToolView for %s" % interface.getName(),
                  (UtilityToolView,),
                  {'interface':interface,
                   'folder':folder,
                   'title':title,
                   'description':description})
    
    view(_context, [class_], IBrowserRequest, name, [ISiteManager],
         permission=permission,
         allowed_interface=[IUtilityToolView, IBrowserPublisher],
         allowed_attributes=['__call__', '__getitem__'])

    class_ = type("UtilityToolAdding for %s" % interface.getName(),
                  (UtilityToolAdding,),
                  {'_addFilterInterface': interface,
                   'folder':folder,
                   'title':'Add %s Tool' % interface.getName()} )

    addView = complexView(_context, ISiteManager, permission, addName,
                          class_=class_)
    addView.page(_context, 'index.html', 'index')
    addView.page(_context, 'action.html', 'action')

    addView()

def servicetool(_context, folder="tools", title=None, description=None):
    name = "manageILocalServiceTool.html"
    addName = "AddServiceTool"
    
    permission = 'zope.ManageContent'

    ifaceDirective(_context, ILocalService, IToolType)

    class_ = type("ServiceToolView",
                  (ServiceToolView,),
                  {'folder':folder,
                   'title':title,
                   'description':description})
    
    view(_context, [class_], IBrowserRequest, name, [ISiteManager],
         permission=permission,
         allowed_interface=[IToolView, IBrowserPublisher],
         allowed_attributes=['__call__', '__getitem__'])

    class_ = type("ServiceToolAdding",
                  (ServiceToolAdding,),
                  {'folder':folder} )

    addView = complexView(_context, ISiteManager, permission, addName,
                          class_=class_)
    addView.page(_context, 'index.html', 'index')
    addView.page(_context, 'action.html', 'action')

    addView()
