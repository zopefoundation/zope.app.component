##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""
$Id$
"""
from zope.interface import Interface
from zope.configuration.fields import GlobalObject, Tokens, \
     PythonIdentifier, MessageID
from zope.schema import TextLine, Id
from zope.app.security.fields import Permission

class IBasicComponentInformation(Interface):

    component = GlobalObject(
        title=u"Component to be used",
        required=False
        )

    permission = Permission(
        title=u"Permission",
        required=False
        )

    factory = GlobalObject(
        title=u"Factory",
        required=False
        )

class IBasicViewInformation(Interface):
    """
    This is the basic information for all views.
    """
    
    for_ = Tokens(
        title=u"Specifications of the objects to be viewed",
        description=u"""This should be a list of interfaces or classes
        """,
        required=True,
        value_type=GlobalObject(missing_value=object())
        )

    permission = Permission(
        title=u"Permission",
        description=u"The permission needed to use the view.",
        required=False
        )

    class_ = GlobalObject(
        title=u"Class",
        description=u"A class that provides attributes used by the view.",
        required=False
        )

    layer = TextLine(
        title=u"The layer the view is in.",
        description=u"""
        A skin is composed of layers. It is common to put skin
        specific views in a layer named after the skin. If the 'layer'
        attribute is not supplied, it defaults to 'default'.""",
        required=False
        )

    allowed_interface = Tokens(
        title=u"Interface that is also allowed if user has permission.",
        description=u"""
        By default, 'permission' only applies to viewing the view and
        any possible sub views. By specifying this attribute, you can
        make the permission also apply to everything described in the
        supplied interface.

        Multiple interfaces can be provided, separated by
        whitespace.""",
        required=False,
        value_type=GlobalObject()
        )

    allowed_attributes = Tokens(
        title=u"View attributes that are also allowed if user has permission.",
        description=u"""
        By default, 'permission' only applies to viewing the view and
        any possible sub views. By specifying 'allowed_attributes',
        you can make the permission also apply to the extra attributes
        on the view object.""",
        required=False,
        value_type=PythonIdentifier()
        )

class IBasicResourceInformation(Interface):
    """
    Basic information for resources
    """

    name = TextLine(
        title=u"The name of the resource.",
        description=u"The name shows up in URLs/paths. For example 'foo'.",
        required=True,
        default=u'',
        )

    provides = GlobalObject(
        title=u"The interface this component provides.",
        description=u"""
        A view can provide an interface.  This would be used for
        views that support other views.""",
        required=False,
        default=Interface,
        )

    type = GlobalObject(
        title=u"Request type",
        required=True
        )

class IInterfaceDirective(Interface):
    """
    Define an interface
    """
    
    interface = GlobalObject(
        title=u"Interface",
        required=True
        )

    type = GlobalObject(
        title=u"Interface type",
        required=False
        )

class IAdapterDirective(Interface):
    """
    Register an adapter
    """

    factory = Tokens(
        title=u"Adapter factory/factories",
        description=u"""A list of factories (usually just one) that create the
        adapter instance.""",
        required=True,
        value_type=GlobalObject()
        )

    provides = GlobalObject(
        title=u"Interface the component provides",
        description=u"""This attribute specifes the interface the adapter
        instance must provide.""",
        required=True
        )

    for_ = Tokens(
        title=u"Specifications to be adapted",
        description=u"""This should be a list of interfaces or classes
        """,
        required=True,
        value_type=GlobalObject(missing_value=object())
        )

    permission = Permission(
        title=u"Permission",
        description=u"""This adapter is only available, if the principal has
        this permission.""",
        required=False
        )

    name = TextLine(
        title=u"Name",
        description=u"""Adapters can have names. This attribute allows you to
        specify the name for this adapter.""",
        required=False
        )

class ISubscriberDirective(Interface):
    """
    Register a subscriber
    """

    factory = GlobalObject(
        title=u"Subscriber factory",
        description=u"A factory used to create the subscriber instance.",
        required=True
        )

    provides = GlobalObject(
        title=u"Interface the component provides",
        description=u"""This attribute specifes the interface the adapter
        instance must provide.""",
        required=False,
        )

    for_ = Tokens(
        title=u"Interfaces or classes that this subscriber depends on",
        description=u"This should be a list of interfaces or classes",
        required=True,
        value_type=GlobalObject(missing_value = object()),
        )

    permission = Permission(
        title=u"Permission",
        description=u"""This subscriber is only available, if the principal has
        this permission.""",
        required=False
        )

class IUtilityDirective(IBasicComponentInformation):
    """
    Register a utility
    """

    provides = GlobalObject(
        title=u"Interface the component provides",
        required=True
        )

    name = TextLine(
        title=u"Name",
        required=False
        )

class IFactoryDirective(Interface):
    """
    Define a factory
    """

    component = GlobalObject(
        title=u"Component to be used",
        required=True
        )
    
    id = TextLine(
        title=u"ID",
        required=False
        )

    title = MessageID(
        title=u"Title",
        description=u"""
        text suitable for use in the 'add content' menu of a
        management interface""",
        required=False
        )

    description = MessageID(
        title=u"Description",
        description=u"Longer narrative description of what this factory does",
        required=False
        )


class IViewDirective(IBasicViewInformation, IBasicResourceInformation):
    """
    Register a view for a component
    """

    factory = Tokens(
        title=u"Factory",
        required=False,
        value_type=GlobalObject()
        )

class IDefaultViewDirective(IBasicResourceInformation):
    """The name of the view that should be the default.

    This name refers to view that should be the
    view used by default (if no view name is supplied
    explicitly).
    """

    for_ = GlobalObject(
        title=u"The interface this view is the default for.",
        description=u"""
        The view is the default view for the supplied interface. If
        this is not supplied, the view applies to all objects (XXX
        this ought to change).""",
        required=False
        )



class IResourceDirective(IBasicComponentInformation,
                         IBasicResourceInformation):
    """
    Register a resource
    """
    
    layer = TextLine(
        title=u"The layer the resource is in.",
        required=False
        )

    allowed_interface = Tokens(
        title=u"Interface that is also allowed if user has permission.",
        required=False,
        value_type=GlobalObject()
        )

    allowed_attributes = Tokens(
        title=u"View attributes that are also allowed if user has permission.",
        required=False,
        value_type=PythonIdentifier()
        )

class ILayerDirective(Interface):
    """
    Register a layer
    """

    name = TextLine(
        title=u"Layer name",
        description=u"Layer name",
        required=True
        )

class ISkinDirective(Interface):
    """
    Register a skin
    """

    name = TextLine(
        title=u"Skin name",
        description=u"Skin name",
        required=True
        )

    layers = Tokens(
        title=u"The layers it consists of.",
        required=True,
        value_type=TextLine()
        )

class IDefaultSkinDirective(Interface):
    """
    Register a skin
    """

    name = TextLine(
        title=u"Default skin name",
        description=u"Default skin name",
        required=True
        )

class IServiceTypeDirective(Interface):

    id = TextLine(
        title=u"ID of the service type",
        required=True
        )

    interface = GlobalObject(
        title=u"Interface of the service type",
        required=True
        )

class IServiceDirective(IBasicComponentInformation):
    """
    Register a service
    """

    serviceType = TextLine(
        title=u"ID of service type",
        required=True
        )

class IClassDirective(Interface):
    """
    Make statements about a class
    """

    class_ = GlobalObject(
        title=u"Class",
        required=True
        )

class IImplementsSubdirective(Interface):
    """
    Declare that the class given by the content directive's class
    attribute implements a given interface
    """

    interface = Tokens(
        title=u"One or more interfaces",
        required=True,
        value_type=GlobalObject()
        )

class IRequireSubdirective(Interface):
    """
    Indicate that the a specified list of names or the names in a
    given Interface require a given permission for access.
    """

    permission = Permission(
        title=u"Permission",
        description=u"""
        Specifies the permission by id that will be required to
        access or mutate the attributes and methods specified.""",
        required=False
        )

    attributes = Tokens(
        title=u"Attributes and methods",
        description=u"""
        This is a list of attributes and methods that can be accessed.""",
        required=False,
        value_type=PythonIdentifier()
        )
        
    set_attributes = Tokens(
        title=u"Attributes that can be set",
        description=u"""
        This is a list of attributes that can be modified/mutated.""",
        required=False,
        value_type=PythonIdentifier()
        )

    interface = Tokens(
        title=u"Interfaces",
        description=u"""
        The listed interfaces' methods and attributes can be accessed.""",
        required=False,
        value_type=GlobalObject()
        )

    set_schema = Tokens(
        title=u"The attributes specified by the schema can be set",
        description=u"""
        The listed schemas' properties can be modified/mutated.""",
        required=False,
        value_type=GlobalObject()
        )

    like_class = GlobalObject(
        title=u"Configure like this class",
        description=u"""
        This argument says that this content class should be configured in the
        same way the specified class' security is. If this argument is
        specifed, no other argument can be used.""",
        required=False
        )
    
class IAllowSubdirective(Interface):
    """
    Declare a part of the class to be publicly viewable (that is,
    requires the zope.Public permission). Only one of the following
    two attributes may be used.
    """

    attributes = Tokens(
        title=u"Attributes",
        required=False,
        value_type=PythonIdentifier()
        )

    interface = Tokens(
        title=u"Interface",
        required=False,
        value_type=GlobalObject()
        )

class IFactorySubdirective(Interface):
    """
    Specify the factory used to create this content object
    """

    id = TextLine(
        title=u"ID",
        description=u"""
        the identifier for this factory in the ZMI factory
        identification scheme.  If not given, defaults to the literal
        string given as the content directive's 'class' attribute.""",
        required=False
        )

    title = MessageID(
        title=u"Title",
        description=u"""
        text suitable for use in the 'add content' menu of a
        management interface""",
        required=False
        )

    description = MessageID(
        title=u"Description",
        description=u"Longer narrative description of what this factory does",
        required=False
        )
