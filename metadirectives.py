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
$Id: metadirectives.py,v 1.6 2003/11/21 17:11:29 jim Exp $
"""

from zope.interface import Interface
from zope.configuration.fields import GlobalObject, Tokens, \
     PythonIdentifier, MessageID
from zope.schema import TextLine, Id

class IBasicComponentInformation(Interface):

    component = GlobalObject(
        title=u"Component to be used",
        required=False
        )

    permission = Id(
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

    for_ = GlobalObject(
        title=u"The interface this view applies to.",
        description=u"""
        The view will be for all objects that implement this
        interface. If this is not supplied, the view applies to all
        objects (XXX this ought to change).""",
        required=False
        )

    permission = Id(
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
        required=True
        )

    type = GlobalObject(
        title=u"Type of the resource",
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

class IAdapterDirective(Interface):
    """
    Register an adapter
    """

    factory = Tokens(
        title=u"Adapter factory/factories",
        required=True,
        value_type=GlobalObject()
        )

    provides = GlobalObject(
        title=u"Interface the component provides",
        required=True
        )

    for_ = GlobalObject(
        title=u"Interface the component is used for",
        required=True
        )

    permission = Id(
        title=u"Permission",
        required=False
        )

    name = TextLine(
        title=u"Name",
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

    permission = Id(
        title=u"Permission",
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

class IResourceDirective(IBasicComponentInformation, IBasicResourceInformation):
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

    permission = Id(
        title=u"Permission",
        required=False
        )

    attributes = Tokens(
        title=u"Attributes",
        required=False,
        value_type=PythonIdentifier()
        )
        
    set_attributes = Tokens(
        title=u"Attributes that can be set",
        required=False,
        value_type=PythonIdentifier()
        )

    interface = Tokens(
        title=u"Interface",
        required=False,
        value_type=GlobalObject()
        )

    set_schema = Tokens(
        title=u"The attributes specified by the schema can be set",
        required=False,
        value_type=GlobalObject()
        )

    like_class = GlobalObject(
        title=u"Configure like this class",
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

    permission = Id(
        title=u"Permission",
        description=u"""
        permission id required to use this factory.  Although
        optional, this attribute should normally be specified.""",
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
