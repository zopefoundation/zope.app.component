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
"""Component architecture related 'zope' ZCML namespace directive interfaces

$Id$
"""
import zope.configuration.fields
import zope.interface
import zope.schema

import zope.app.security.fields

class IBasicComponentInformation(zope.interface.Interface):

    component = zope.configuration.fields.GlobalObject(
        title=u"Component to be used",
        required=False
        )

    permission = zope.app.security.fields.Permission(
        title=u"Permission",
        required=False
        )

    factory = zope.configuration.fields.GlobalObject(
        title=u"Factory",
        required=False
        )

class IBasicViewInformation(zope.interface.Interface):
    """This is the basic information for all views."""
    
    for_ = zope.configuration.fields.Tokens(
        title=u"Specifications of the objects to be viewed",
        description=u"""This should be a list of interfaces or classes
        """,
        required=True,
        value_type=zope.configuration.fields.GlobalObject(
          missing_value=object(),
          ),
        )

    permission = zope.app.security.fields.Permission(
        title=u"Permission",
        description=u"The permission needed to use the view.",
        required=False
        )

    class_ = zope.configuration.fields.GlobalObject(
        title=u"Class",
        description=u"A class that provides attributes used by the view.",
        required=False
        )

    layer = zope.schema.TextLine(
        title=u"The layer the view is in.",
        description=u"""
        A skin is composed of layers. It is common to put skin
        specific views in a layer named after the skin. If the 'layer'
        attribute is not supplied, it defaults to 'default'.""",
        required=False
        )

    allowed_interface = zope.configuration.fields.Tokens(
        title=u"Interface that is also allowed if user has permission.",
        description=u"""
        By default, 'permission' only applies to viewing the view and
        any possible sub views. By specifying this attribute, you can
        make the permission also apply to everything described in the
        supplied interface.

        Multiple interfaces can be provided, separated by
        whitespace.""",
        required=False,
        value_type=zope.configuration.fields.GlobalObject()
        )

    allowed_attributes = zope.configuration.fields.Tokens(
        title=u"View attributes that are also allowed if user has permission.",
        description=u"""
        By default, 'permission' only applies to viewing the view and
        any possible sub views. By specifying 'allowed_attributes',
        you can make the permission also apply to the extra attributes
        on the view object.""",
        required=False,
        value_type=zope.configuration.fields.PythonIdentifier()
        )

class IBasicResourceInformation(zope.interface.Interface):
    """
    Basic information for resources
    """

    name = zope.schema.TextLine(
        title=u"The name of the resource.",
        description=u"The name shows up in URLs/paths. For example 'foo'.",
        required=True,
        default=u'',
        )

    provides = zope.configuration.fields.GlobalObject(
        title=u"The interface this component provides.",
        description=u"""
        A view can provide an interface.  This would be used for
        views that support other views.""",
        required=False,
        default=zope.interface.Interface,
        )

    type = zope.configuration.fields.GlobalObject(
        title=u"Request type",
        required=True
        )

class IInterfaceDirective(zope.interface.Interface):
    """
    Define an interface
    """
    
    interface = zope.configuration.fields.GlobalObject(
        title=u"Interface",
        required=True
        )

    type = zope.configuration.fields.GlobalObject(
        title=u"Interface type",
        required=False
        )

class IAdapterDirective(zope.interface.Interface):
    """
    Register an adapter
    """

    factory = zope.configuration.fields.Tokens(
        title=u"Adapter factory/factories",
        description=u"""A list of factories (usually just one) that create the
        adapter instance.""",
        required=True,
        value_type=zope.configuration.fields.GlobalObject()
        )

    provides = zope.configuration.fields.GlobalObject(
        title=u"Interface the component provides",
        description=u"""This attribute specifes the interface the adapter
        instance must provide.""",
        required=True
        )

    for_ = zope.configuration.fields.Tokens(
        title=u"Specifications to be adapted",
        description=u"""This should be a list of interfaces or classes
        """,
        required=True,
        value_type=zope.configuration.fields.GlobalObject(
          missing_value=object(),
          ),
        )

    permission = zope.app.security.fields.Permission(
        title=u"Permission",
        description=u"""This adapter is only available, if the principal has
        this permission.""",
        required=False
        )

    name = zope.schema.TextLine(
        title=u"Name",
        description=u"""Adapters can have names.

        This attribute allows you to
        specify the name for this adapter.""",
        required=False
        )

    trusted = zope.configuration.fields.Bool(
        title=u"Trusted",
        description=u"""Make the adapter a trusted adapter

        Trusted adapters have unfettered access to the objects they
        adapt.  If asked to adapt security-proxied objects, then,
        rather than getting an unproxied adapter of security-proxied
        objects, you get a security-proxied adapter of unproxied
        objects.
        """,
        required=False,
        default=False,
        )

class ISubscriberDirective(zope.interface.Interface):
    """
    Register a subscriber
    """

    factory = zope.configuration.fields.GlobalObject(
        title=u"Subscriber factory",
        description=u"A factory used to create the subscriber instance.",
        required=True
        )

    provides = zope.configuration.fields.GlobalObject(
        title=u"Interface the component provides",
        description=u"""This attribute specifes the interface the adapter
        instance must provide.""",
        required=False,
        )

    for_ = zope.configuration.fields.Tokens(
        title=u"Interfaces or classes that this subscriber depends on",
        description=u"This should be a list of interfaces or classes",
        required=True,
        value_type=zope.configuration.fields.GlobalObject(
          missing_value = object(),
          ),
        )

    permission = zope.app.security.fields.Permission(
        title=u"Permission",
        description=u"""This subscriber is only available, if the principal has
        this permission.""",
        required=False
        )

    trusted = zope.configuration.fields.Bool(
        title=u"Trusted",
        description=u"""Make the subscriber a trusted subscriber

        Trusted subscribers have unfettered access to the objects they
        adapt.  If asked to adapt security-proxied objects, then,
        rather than getting an unproxied subscriber of security-proxied
        objects, you get a security-proxied subscriber of unproxied
        objects.
        """,
        required=False,
        default=False,
        )

class IUtilityDirective(IBasicComponentInformation):
    """Register a utility"""

    provides = zope.configuration.fields.GlobalObject(
        title=u"Interface the component provides",
        required=True
        )

    name = zope.schema.TextLine(
        title=u"Name",
        required=False
        )

class IFactoryDirective(zope.interface.Interface):
    """Define a factory"""

    component = zope.configuration.fields.GlobalObject(
        title=u"Component to be used",
        required=True
        )
    
    id = zope.schema.Id(
        title=u"ID",
        required=False
        )

    title = zope.configuration.fields.MessageID(
        title=u"Title",
        description=u"""
        text suitable for use in the 'add content' menu of a
        management interface""",
        required=False
        )

    description = zope.configuration.fields.MessageID(
        title=u"Description",
        description=u"Longer narrative description of what this factory does",
        required=False
        )


class IViewDirective(IBasicViewInformation, IBasicResourceInformation):
    """Register a view for a component"""

    factory = zope.configuration.fields.Tokens(
        title=u"Factory",
        required=False,
        value_type=zope.configuration.fields.GlobalObject()
        )

class IDefaultViewDirective(IBasicResourceInformation):
    """The name of the view that should be the default.

    This name refers to view that should be the
    view used by default (if no view name is supplied
    explicitly).
    """

    for_ = zope.configuration.fields.GlobalObject(
        title=u"The interface this view is the default for.",
        description=u"""
        Specifies the interface for which the default view is declared. All
        objects implementing this interface make use of this default
        setting. If this attribute is not specified, the default is available
        for all objects.""",
        required=False
        )



class IResourceDirective(IBasicComponentInformation,
                         IBasicResourceInformation):
    """Register a resource"""
    
    layer = zope.schema.TextLine(
        title=u"The layer the resource is in.",
        required=False
        )

    allowed_interface = zope.configuration.fields.Tokens(
        title=u"Interface that is also allowed if user has permission.",
        required=False,
        value_type=zope.configuration.fields.GlobalObject()
        )

    allowed_attributes = zope.configuration.fields.Tokens(
        title=u"View attributes that are also allowed if user has permission.",
        required=False,
        value_type=zope.configuration.fields.PythonIdentifier()
        )


class IServiceTypeDirective(zope.interface.Interface):

    id = zope.schema.TextLine(
        title=u"ID of the service type",
        required=True
        )

    interface = zope.configuration.fields.GlobalObject(
        title=u"Interface of the service type",
        required=True
        )

class IServiceDirective(IBasicComponentInformation):
    """Register a service"""

    serviceType = zope.schema.TextLine(
        title=u"ID of service type",
        required=True
        )

class IClassDirective(zope.interface.Interface):
    """Make statements about a class"""

    class_ = zope.configuration.fields.GlobalObject(
        title=u"Class",
        required=True
        )

class IImplementsSubdirective(zope.interface.Interface):
    """Declare that the class given by the content directive's class
    attribute implements a given interface
    """

    interface = zope.configuration.fields.Tokens(
        title=u"One or more interfaces",
        required=True,
        value_type=zope.configuration.fields.GlobalObject()
        )

class IRequireSubdirective(zope.interface.Interface):
    """Indicate that the a specified list of names or the names in a
    given Interface require a given permission for access.
    """

    permission = zope.app.security.fields.Permission(
        title=u"Permission",
        description=u"""
        Specifies the permission by id that will be required to
        access or mutate the attributes and methods specified.""",
        required=False
        )

    attributes = zope.configuration.fields.Tokens(
        title=u"Attributes and methods",
        description=u"""
        This is a list of attributes and methods that can be accessed.""",
        required=False,
        value_type=zope.configuration.fields.PythonIdentifier()
        )
        
    set_attributes = zope.configuration.fields.Tokens(
        title=u"Attributes that can be set",
        description=u"""
        This is a list of attributes that can be modified/mutated.""",
        required=False,
        value_type=zope.configuration.fields.PythonIdentifier()
        )

    interface = zope.configuration.fields.Tokens(
        title=u"Interfaces",
        description=u"""
        The listed interfaces' methods and attributes can be accessed.""",
        required=False,
        value_type=zope.configuration.fields.GlobalObject()
        )

    set_schema = zope.configuration.fields.Tokens(
        title=u"The attributes specified by the schema can be set",
        description=u"""
        The listed schemas' properties can be modified/mutated.""",
        required=False,
        value_type=zope.configuration.fields.GlobalObject()
        )

    like_class = zope.configuration.fields.GlobalObject(
        title=u"Configure like this class",
        description=u"""
        This argument says that this content class should be configured in the
        same way the specified class' security is. If this argument is
        specifed, no other argument can be used.""",
        required=False
        )
    
class IAllowSubdirective(zope.interface.Interface):
    """
    Declare a part of the class to be publicly viewable (that is,
    requires the zope.Public permission). Only one of the following
    two attributes may be used.
    """

    attributes = zope.configuration.fields.Tokens(
        title=u"Attributes",
        required=False,
        value_type=zope.configuration.fields.PythonIdentifier()
        )

    interface = zope.configuration.fields.Tokens(
        title=u"Interface",
        required=False,
        value_type=zope.configuration.fields.GlobalObject()
        )

class IFactorySubdirective(zope.interface.Interface):
    """Specify the factory used to create this content object"""

    id = zope.schema.Id(
        title=u"ID",
        description=u"""
        the identifier for this factory in the ZMI factory
        identification scheme.  If not given, defaults to the literal
        string given as the content directive's 'class' attribute.""",
        required=False
        )

    title = zope.configuration.fields.MessageID(
        title=u"Title",
        description=u"""
        text suitable for use in the 'add content' menu of a
        management interface""",
        required=False
        )

    description = zope.configuration.fields.MessageID(
        title=u"Description",
        description=u"Longer narrative description of what this factory does",
        required=False
        )
