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
"""Interface field widget tests

$Id: test_interfacewidget.py,v 1.1 2004/03/14 00:15:19 srichter Exp $
"""
from zope.interface import Interface
from unittest import TestCase, TestSuite, makeSuite
from zope.app.component.interfacefield import InterfaceField, InterfacesField
from zope.app.component.browser.interfacewidget import InterfaceWidget
from zope.app.component.browser.interfacewidget import MultiInterfaceWidget
from zope.publisher.browser import TestRequest
from zope.app.form.interfaces import ConversionError, WidgetInputError
from zope.app.tests import placelesssetup
from zope.app.component.interface import getInterface, provideInterface
    
class I(Interface):
    """bah blah
    """

class I2(Interface):
    """eek
    """

class I3(Interface):
    """ahk
    """
    def one():
        """method one"""

    def two():
        """method two"""

class BaseInterfaceWidgetTest(TestCase):

    def setUp(self):
        placelesssetup.setUp()
        provideInterface(
            'zope.app.component.browser.tests.test_interfacewidget.I', I)
        provideInterface(
            'zope.app.component.browser.tests.test_interfacewidget.I2', I2)
        provideInterface(
            'zope.app.component.browser.tests.test_interfacewidget.I3', I3)
        request = TestRequest()
        self.request = request

    def tearDown(self):
        placelesssetup.tearDown()
        

class TestInterfaceWidget(BaseInterfaceWidgetTest):

    def testInterfaceWidget(self):
        request = self.request
        field = InterfaceField(__name__='TestName',
                               title=u"This is a test",
                               required=False)

        widget = InterfaceWidget(field, request)

        self.failIf(widget.hasInput())
        self.assertRaises(WidgetInputError, widget.getInputValue)

        out = (
        '<input type="text" name="field.TestName.search" value="">'
        '<select name="field.TestName">'
        '<option value="">---select interface---</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )

        self.assertEqual(widget(), out)

        out = (
        '<input type="text" name="field.TestName.search" value="">'
        '<select name="field.TestName">'
        '<option value="">---select interface---</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '" selected>'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )

        self.failIf(widget.hasInput())
        self.assertRaises(WidgetInputError, widget.getInputValue)

        widget = InterfaceWidget(field, request)

        request.form["field.TestName"] = (
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        )
        self.assertEqual(widget.getInputValue(), I2)
        self.failUnless(widget.hasInput())

        out = (
        '<input type="text" name="field.TestName.search" value="">'
        '<select name="field.TestName">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '" selected>'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )
        
        self.assertEqual(widget(), out)

        request.form["field.TestName.search"] = 'two'
        out = (
        '<input type="text" name="field.TestName.search" value="two">'
        '<select name="field.TestName">'
        '<option value="">---select interface---</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )

        self.assertEqual(widget(), out)

    def testInterfaceWidget_search(self):
        field = InterfaceField(__name__='TestName',
                               title=u"This is a test",
                               required=True)

        request = TestRequest(form={'field.TestName': '',
                                    'field.TestName.search': '2',
                                    })
        widget = InterfaceWidget(field, request)


        out = (
        '<input type="text" name="field.TestName.search" value="2">'
        '<select name="field.TestName">'
        '<option value="">---select interface---</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '</option>'

        '</select>'
        )

        self.assertEqual(widget(), out)

    def testInterfaceWidget_w_constraint(self):
        request = self.request
        field = InterfaceField(
            __name__='TestName',
            title=u"This is a test",
            required=False,
            constraint=lambda i: not (i.getName().endswith("2")),
            )

        widget = InterfaceWidget(field, request)

        self.failIf(widget.hasInput())
        self.assertRaises(WidgetInputError, widget.getInputValue)

        out = (
        '<input type="text" name="field.TestName.search" value="">'
        '<select name="field.TestName">'
        '<option value="">---select interface---</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )

        self.assertEqual(widget(), out)

    def testInterfaceWidget_allow_None_as_well_as_interfaces(self):
        request = self.request
        field = InterfaceField(__name__='TestName',
                               title=u"This is a test",
                               basetype=None)

        widget = InterfaceWidget(field, request)

        self.failIf(widget.hasInput())
        self.assertRaises(WidgetInputError, widget.getInputValue)

        out = (
        '<input type="text" name="field.TestName.search" value="">'
        '<select name="field.TestName">'
        '<option value="">---select interface---</option>'

        '<option value="'
        'None'
        '">'
        'any-interface'
        '</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )

        self.assertEqual(widget(), out)

        request.form["field.TestName"] = (
        'None'
        )
        self.assertEqual(widget.getInputValue(), None)
        self.failUnless(widget.hasInput())

        out = (
        '<input type="text" name="field.TestName.search" value="">'
        '<select name="field.TestName">'
        '<option value="">---select interface---</option>'

        '<option value="'
        'None'
        '" selected>'
        'any-interface'
        '</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )

        self.assertEqual(widget(), out)

        # test that None / Anything disappears when there is a search string

        request.form["field.TestName.search"] = (
        'two'
        )

        out = (
        '<input type="text" name="field.TestName.search" value="two">'
        '<select name="field.TestName">'
        '<option value="">---select interface---</option>'

        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )

        self.assertEqual(widget(), out)


    def testBadInterfaceName(self):
        request = self.request
        field = InterfaceField(__name__='TestName',
                               title=u"This is a test",
                               required=False)

        widget = InterfaceWidget(field, request)

        request.form["field.TestName"] = ('bad interface name')
        self.assertRaises(ConversionError, widget.getInputValue)

    def testHidden(self):
        request = self.request
        field = InterfaceField(__name__='TestName',
                               title=u"This is a test",
                               required=False)
        widget = InterfaceWidget(field, request)

        out = (
        '<input type="hidden" name="field.TestName" value="None" />'
        )
        self.assertEqual(widget.hidden(), out)
        
        request.form["field.TestName"] = (
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        )

        self.assertEqual(widget.getInputValue(), I2)
        out = (
        '<input type="hidden" name="field.TestName"'
        ' value="zope.app.component.browser.tests.test_interfacewidget.I2" />'
        )
        self.assertEqual(widget.hidden(), out)

    def testHiddenNone(self):
        request = self.request
        field = InterfaceField(__name__='TestName',
                               title=u"This is a test",
                               basetype=None)

        widget = InterfaceWidget(field, request)

        out = (
        '<input type="hidden" name="field.TestName" value="None" />'
        )
        self.assertEqual(widget.hidden(), out)

        request.form["field.TestName"] = (
        'None'
        )
        self.assertEqual(widget.getInputValue(), None)
        out = (
        '<input type="hidden" name="field.TestName" value="None" />'
        )
        self.assertEqual(widget.hidden(), out)


# XXX Note that MultiInterface widgets should be for multi-interface fields

class TestMultiInterfaceWidget(BaseInterfaceWidgetTest):

    def testMultiInterfaceWidget(self):
        request = self.request
        field = InterfacesField(__name__='TestName',
                                title=u'This is a test',
                                required=False)
        widget = MultiInterfaceWidget(field, request)

        self.failIf(widget.hasInput())
        self.assertRaises(WidgetInputError, widget.getInputValue)

        out = (
        'Use refresh to enter more interfaces'
        '<br />'

        '<input type="text" name="field.TestName.search.i0" value="">'

        '<select name="field.TestName.i0">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'

        '<br />'

        '<input type="text" name="field.TestName.search.i1" value="">'

        '<select name="field.TestName.i1">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )
        self.assertEqual(widget(), out)
        self.failIf(widget.hasInput())

        widget = MultiInterfaceWidget(field, request)

        request.form["field.TestName.i1"] = (
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        )
        self.assertEqual(widget.getInputValue(), (I2,))
        self.failUnless(widget.hasInput())
        out = (
        'Use refresh to enter more interfaces'
        '<br />'

        '<input type="text" name="field.TestName.search.i0" value="">'

        '<select name="field.TestName.i0">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'

        '<br />'
        '<input type="text" name="field.TestName.search.i1" value="">'

        '<select name="field.TestName.i1">'
        '<option value="">---select interface---</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '" selected>'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )
        self.assertEqual(widget(), out)
        self.failUnless(widget.hasInput())

        # There is no selected option because the option that would be
        # selected has been filtered out by the search.
        request.form["field.TestName.search.i1"] = 'two'
        out = (
        'Use refresh to enter more interfaces'
        '<br />'

        '<input type="text" name="field.TestName.search.i0" value="">'

        '<select name="field.TestName.i0">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'

        '<br />'

        '<input type="text" name="field.TestName.search.i1" value="two">'

        '<select name="field.TestName.i1">'
        '<option value="">---select interface---</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )
        self.assertEqual(widget(), out)
        self.failUnless(widget.hasInput())
        label = '<label for="field.TestName">This is a test</label>'
        self.assertEqual(widget.label(), label)
        self.assertEqual(widget.row(),
                         '<div class="label">%s</div>'
                         '<div class="field">%s</div>' % (label, out)
                         )

    def testMultiInterfaceWidgetNone(self):
        request = self.request
        field = InterfacesField(__name__='TestName',
                                title=u'This is a test',
                                basetype=None)
        widget = MultiInterfaceWidget(field, request)

        self.failIf(widget.hasInput())
        self.assertRaises(WidgetInputError, widget.getInputValue)

        out = (
        'Use refresh to enter more interfaces'
        '<br />'

        '<input type="text" name="field.TestName.search.i0" value="">'

        '<select name="field.TestName.i0">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'None'
        '">'
        'any-interface'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'

        '<br />'

        '<input type="text" name="field.TestName.search.i1" value="">'

        '<select name="field.TestName.i1">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'None'
        '">'
        'any-interface'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )
        self.assertEqual(widget(), out)

        request.form["field.TestName.i1"] = 'None'
        self.assertEqual(widget.getInputValue(), (None,))
        self.failUnless(widget.hasInput())

        out = (
        'Use refresh to enter more interfaces'
        '<br />'

        '<input type="text" name="field.TestName.search.i0" value="">'

        '<select name="field.TestName.i0">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'None'
        '">'
        'any-interface'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'

        '<br />'

        '<input type="text" name="field.TestName.search.i1" value="">'

        '<select name="field.TestName.i1">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'None'
        '" selected>'
        'any-interface'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )
        self.assertEqual(widget(), out)

        # test that None / Anything disappears when there is a search string

        request.form["field.TestName.search.i1"] = 'two'

        out = (
        'Use refresh to enter more interfaces'
        '<br />'

        '<input type="text" name="field.TestName.search.i0" value="">'

        '<select name="field.TestName.i0">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'None'
        '">'
        'any-interface'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'

        '<br />'

        '<input type="text" name="field.TestName.search.i1" value="two">'

        '<select name="field.TestName.i1">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '">'
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )
        self.assertEqual(widget(), out)

    def testBadInterfaceName(self):
        request = self.request
        field = InterfaceField(__name__='TestName',
                               title=u"This is a test",
                               required=False)

        widget = MultiInterfaceWidget(field, request)

        request.form["field.TestName.i0"] = ('bad interface name')
        self.assertRaises(ConversionError, widget.getInputValue)

    def testHidden(self):
        request = self.request
        field = InterfacesField(__name__='TestName',
                                title=u"This is a test",
                                required=False)

        widget = MultiInterfaceWidget(field, request)

        self.assertEqual(widget.hidden(), '')

        request.form["field.TestName.i0"] = (
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        )
        self.assertEqual(widget.getInputValue(), (I2,))
        out = (
        '<input type="hidden" name="field.TestName.i0"'
        ' value="zope.app.component.browser.tests.test_interfacewidget.I2" />'
        )
        self.assertEqual(widget.hidden(), out)

        request.form["field.TestName.i1"] = (
        'zope.app.component.browser.tests.test_interfacewidget.I3'
        )
        self.assertEqual(widget.getInputValue(), (I2, I3))
        out = (
        '<input type="hidden" name="field.TestName.i0"'
        ' value="zope.app.component.browser.tests.test_interfacewidget.I2" />'
        '<input type="hidden" name="field.TestName.i1"'
        ' value="zope.app.component.browser.tests.test_interfacewidget.I3" />'
        )
        self.assertEqual(widget.hidden(), out)

    def testHiddenNone(self):
        request = self.request
        field = InterfacesField(__name__='TestName',
                                title=u"This is a test",
                                basetype=None)

        widget = MultiInterfaceWidget(field, request)

        self.assertEqual(widget.hidden(), '')

        request.form["field.TestName.i0"] = (
        'None'
        )
        self.assertEqual(widget.getInputValue(), (None,))
        out = (
        '<input type="hidden" name="field.TestName.i0" value="None" />'
        )
        self.assertEqual(widget.hidden(), out)

    def testEmptyFormData(self):
        request = self.request
        field = InterfacesField(__name__='TestName',
                                title=u'This is a test',
                                required=False)
        widget = MultiInterfaceWidget(field, request)

        self.failIf(widget.hasInput())
        self.assertRaises(WidgetInputError, widget.getInputValue)

        request.form["field.TestName.i1"] = (
        'zope.app.component.browser.tests.test_interfacewidget.I2'
        )
        request.form["field.TestName.i0"] = ''
        self.assertEqual(widget.getInputValue(), (I2,))
        self.failUnless(widget.hasInput())

class TestRenderInterfaceSelect(TestCase):

    def testInterfaceSelect(self):
        from zope.app.component.browser.interfacewidget \
            import renderInterfaceSelect
        interfaces = ['foo', 'bar', 'baz']
        selected = 'bar'
        search_name = 'searchname'
        search_string = 'foo"blee'
        select_name = 'selectname'
        out = (
        '''<input type="text" name="searchname" value=\'foo"blee\'>'''
        '''<select name="selectname">'''
        '''<option value="">---select interface---</option>'''
        '''<option value="foo">foo</option>'''
        '''<option value="bar" selected>bar</option>'''
        '''<option value="baz">baz</option>'''
        '''</select>'''
        )
        self.assertEqual(
            renderInterfaceSelect(interfaces, selected, search_name,
                                  search_string, select_name),
            out)

    def testEmptyInterfaceSelect(self):
        from zope.app.component.browser.interfacewidget \
            import renderInterfaceSelect
        interfaces = []
        selected = 'bar'
        search_name = 'searchname'
        search_string = 'fooblee'
        select_name = 'selectname'
        out = (
        '<input type="text" name="searchname" value="fooblee">'
        '<select name="selectname">'
        '<option value="">---select interface---</option>'
        '</select>'
        )
        self.assertEqual(
            renderInterfaceSelect(interfaces, selected, search_name,
                                  search_string, select_name),
            out)
    
def test_suite():
    return TestSuite((makeSuite(TestInterfaceWidget),
                      makeSuite(TestMultiInterfaceWidget),
                      makeSuite(TestRenderInterfaceSelect),
                    ))
