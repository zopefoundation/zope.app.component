##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Interface widgets

$Id: interfacewidget.py,v 1.4 2004/03/19 20:26:23 srichter Exp $
"""
from xml.sax.saxutils import quoteattr

from zope.interface import Interface, implements
from zope.app.publisher.browser import BrowserView
from zope.component import getService
from zope.component.exceptions import ComponentLookupError

from zope.app.form.browser.widget import BrowserWidget
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.form.interfaces import IInputWidget, WidgetInputError
from zope.app.form.interfaces import ConversionError, MissingInputError
from zope.app.introspector import interfaceToName
from zope.app.component.interface import searchInterfaceIds, nameToInterface
from zope.app.component.interface import searchInterface

class InterfaceWidget(BrowserWidget, BrowserView):

    implements(IInputWidget)

    def _convert(self, value):
        if value and value != 'None':
            try:
                field = self.context
                return nameToInterface(field, value)
            except ComponentLookupError, e:
                raise ConversionError('unknown interface', e)
        else:
            return None


    def __call__(self):
        name = self.name
        search_name = name + ".search"
        search_string = self.request.form.get(search_name, '')

        field = self.context
        base = field.basetype
        include_none = base is None
        if base == Interface:
            base = None
        items = list(searchInterface(self.context, search_string, base=base))
        if field.constraint is not None:
            items = [iface
                     for iface in items
                     if field.constraint(iface)
                     ]
        ids = [('%s.%s' %(iface.__module__, iface.__name__))
               for iface in items
               ]
        ids.sort()
        # Only include None if there is no search string, and include_none
        # is True
        if include_none and not search_string:
            ids = ['None'] + ids

        marker = self
        if field.default:
            selected = field.default
        else:
            selected = marker
        if not self._renderedValueSet():
            value = self.request.form.get(self.name, marker) or marker
            if value is not marker:
                try:
                    selected = self.getInputValue()
                except WidgetInputError, e:
                    self._error = e
                    selected = value
        else:
            selected = self._data

        if selected is not marker:
            selected = interfaceToName(field.context, selected)
        return renderInterfaceSelect(
                ids, selected, search_name, search_string, name)

    def hidden(self):
        'See IBrowserWidget'
        field = self.context
        try:
            iface = self.getInputValue()
        except WidgetInputError:
            iface = None
        return '<input type="hidden" name="%s" value="%s" />' % \
            (self.name, interfaceToName(field.context, iface))


# A MultiInterfaceWidget is for use with an InterfacesField,
# which is a tuple of interfaces.
class MultiInterfaceWidget(BrowserWidget, BrowserView):

    implements(IInputWidget)

    # Names used:
    #
    #  name.i0, name.i1, ...  the value of the interfaces
    #  name.search.i0, ...    the search box for that interface
    #
    def hasInput(self):
        name_i = self.name+'.i'
        field = self.context
        for k,v in self.request.form.iteritems():
            if k.startswith(name_i):
                if v and (v == 'None' or nameToInterface(field, v)):
                    return True
        return False


    def getInputValue(self):
        field = self.context
        name_i = self.name+'.i'
        items_sorted = self.request.form.items()
        items_sorted.sort()
        # values will be sorted in key order
        values = [v
                  for k,v in items_sorted
                  if k.startswith(name_i)
                  if v]

        # form input is required, otherwise raise an error
        if not values:
            raise MissingInputError(self.name, self.title, None)    # XXX

        # convert input to a tuple of interfaces
        try:
            values = [nameToInterface(field, value) for value in values]
            return tuple(values)
        except ComponentLookupError, e:
            raise ConversionError('unknown interface', e)


    def __call__(self):
        'See IBrowserWidget'
        field = self.context
        form = self.request.form
        name = self.name
        name_i = name+'.i'
        name_search_i = name+'.search.i'
        base = field.basetype
        include_none = base is None
        if base == Interface:
            base = None

        first_is_blank = False
        if self._data is self._data_marker:  # no data has been set with 
                                             # Widget.setRenderedValue(),
                                             # so use the data in the form

            # If a search term is entered, that interface selection remains.
            # If an interface is selected, that interface selection remains.
            # Remove all others.
            # Make sure there is at least one empty selection.
            # Make sure there are at least two selections in total.

            selections = {}  # index:[search, value]
            for k,v in form.iteritems():
                if k.startswith(name_i):
                    index = int(k[len(name_i):])
                    selection = selections.setdefault(index, ['', ''])
                    selection[1] = v
                elif k.startswith(name_search_i):
                    index = int(k[len(name_search_i):])
                    selection = selections.setdefault(index, ['', ''])
                    selection[0] = v.strip()

            # remove all of the selections that have no search and no value
            for k,(s,v) in selections.items():
                if s == v == '':
                    del selections[k]

            if selections:
                selections = selections.items()
                selections.sort()

                # If the first selection really was blank, then remember this
                # fact. We'll use it later if we need to add in an extra
                # selection box: we can add it at the beginning to preserve
                # the order as the user might expect.
                if selections[0][0] != 0:
                    first_is_blank = True

                # get just [search, value], and discard the keys
                selections = [v for k,v in selections]
                # XXX is validation here really needed?
                field.validate(tuple([nameToInterface(field, v)
                                      for s,v in selections
                                      if v != '']))
            else:  # otherwise, use the default
                selections = [('', interfaceToName(field.context, interface))
                              for interface in field.default]
        else:
            # data has been set with Widget.setRenderedValue()
            selections = [('', interfaceToName(field.context, interface))
                          for interface in self._data]

        # If there are no empty values, add one extra empty selection
        if not [1 for s,v in selections if v == '']:
            # if first_is_blank, put the empty selection at the start
            if first_is_blank:
                selections = [['', None]] + selections
            else:
                selections.append(['', None])
        # If there is only one value, add another one. We want at least
        # two values so that it is obvious this is a multi-value selection.
        if len(selections) == 1:
            selections.append(['', None])
        rendered_selections = []
        count = 0
        for search, value in selections:
            ids = list(searchInterfaceIds(self.context, search, base=base))
            ids.sort()
            # Only include None if there is no search string, and include_none
            # is True
            if include_none and not search:
                ids = ['None'] + ids
            search_name = '%s.search.i%s' % (name, count)
            rendered_selections.append(
                renderInterfaceSelect(ids, value, search_name,
                                      search, '%s.i%s' % (name, count))
                )
            count += 1

        HTML = (_(u'Use refresh to enter more interfaces') + '<br />' +
                '<br />'.join(rendered_selections))
        return HTML

    def hidden(self):
        'See IBrowserWidget'
        field = self.context
        if self._data is self._data_marker:
            try:
                data = self.getInputValue()
            except WidgetInputError:
                data = self.request.form.get(self.name, '')
        else:
            data = self._data
        name = self.name
        elements = []
        count = 0
        for interface in data:
            elements.append(
                '<input type="hidden" name="%s.i%s" value="%s" />'
                % (name, count, interfaceToName(field.context, interface))
                )
            count += 1
        return ''.join(elements)


class InterfaceDisplayWidget(InterfaceWidget):
    def __call__(self):
        field = self.context
        if self._data is self._data_marker:
            try:
                data = self.getInputValue()
            except WidgetInputError:
                data = self.request.form.get(self.name, '')
        else:
            data = self._data
        return interfaceToName(field.context, data)
        

class MultiInterfaceDisplayWidget(MultiInterfaceWidget):
    def __call__(self):
        field = self.context
        if self._data is self._data_marker:
            data = self._showData()
        else:
            data = self._data
        return ', '.join([interfaceToName(field.context, interface)
                          for interface in data])
                          

def renderInterfaceSelect(
        interfaces, selected, search_name, search_string, select_name):
    """interfaces is a sequence, all of the other args are strings"""
    options = ['<option value="">' + _(u"---select interface---") + \
               '</option>']
    for interface in interfaces:
        if interface == 'None':
            options.append('<option value="None"%s>' \
                % (interface == selected and ' selected' or '') \
                + _('any-interface', "Anything") + '</option>'

                           )
        else:
            options.append('<option value="%s"%s>%s</option>'
                           % (interface,
                              interface == selected and ' selected' or '',
                              interface)
                           )
    search_field = '<input type="text" name="%s" value=%s>' % (
        search_name, quoteattr(search_string))
    select_field = '<select name="%s">%s</select>'  % (
        select_name, ''.join(options))

    HTML = search_field + select_field
    return HTML

