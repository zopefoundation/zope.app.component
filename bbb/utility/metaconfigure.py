##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Local Utility Directive

$Id$
"""
__docformat__ = "reStructuredText"
from persistent.interfaces import IPersistent
from zope.configuration.exceptions import ConfigurationError
from zope.interface import classImplements

from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.component.contentdirective import ContentDirective
from zope.app.location.interfaces import ILocation

from interfaces import ILocalUtility


class LocalUtilityDirective(ContentDirective):
    r"""localUtility directive handler.

    Examples:

      >>> from zope.interface import implements
      >>> class LU1(object):
      ...     pass

      >>> class LU2(LU1):
      ...     implements(ILocation)

      >>> class LU3(LU1):
      ...     __parent__ = None

      >>> class LU4(LU2):
      ...     implements(IPersistent)

      >>> dir = LocalUtilityDirective(None, LU4)
      >>> IAttributeAnnotatable.implementedBy(LU4)
      True
      >>> ILocalUtility.implementedBy(LU4)
      True

      >>> LocalUtilityDirective(None, LU3)
      Traceback (most recent call last):
      ...
      ConfigurationError: Class `LU3` does not implement `IPersistent`.

      >>> LocalUtilityDirective(None, LU2)
      Traceback (most recent call last):
      ...
      ConfigurationError: Class `LU2` does not implement `IPersistent`.

      >>> LocalUtilityDirective(None, LU1)
      Traceback (most recent call last):
      ...
      ConfigurationError: Class `LU1` does not implement `ILocation`.
    """

    def __init__(self, _context, class_):
        if not ILocation.implementedBy(class_) and \
               not hasattr(class_, '__parent__'):
            raise ConfigurationError, \
                  'Class `%s` does not implement `ILocation`.' %class_.__name__

        if not IPersistent.implementedBy(class_):
            raise ConfigurationError, \
                 'Class `%s` does not implement `IPersistent`.' %class_.__name__

        classImplements(class_, IAttributeAnnotatable)
        classImplements(class_, ILocalUtility)

        super(LocalUtilityDirective, self).__init__(_context, class_)
