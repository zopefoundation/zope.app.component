#############################################################################
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
"""Component-related fields

$Id$
"""
__docformat__ = 'restructuredtext'

# BBB this module can be deleted in 3.3
import sys
# hack to let apidoc dynamically load all modules without complaining
if 'apidoc' not in sys._getframe(10).f_code.co_filename:
    import warnings
    warnings.warn(
        "The class zope.app.component.fields.LayerField is deprecated and will "
        "away in ZopeX3 3.3. Use zope.app.publisher.browser.fields.LayerField "
        "instead.",
        DeprecationWarning)

from zope.app.publisher.browser.fields import LayerField
