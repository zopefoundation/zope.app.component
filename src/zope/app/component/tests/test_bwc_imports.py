#############################################################################
#
# Copyright (c) 2017 Zope Foundation and Contributors.
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

import importlib
import unittest


def _make_import_test(mod_name, attrname):
    def test(self):
        mod = importlib.import_module('zope.app.component.' + mod_name)
        self.assertIsNotNone(getattr(mod, attrname))

    return test


class TestBWCImports(unittest.TestCase):

    for mod_name, attrname in (('contentdirective', 'ClassDirective'),
                               ('hooks', 'read_property'),
                               ('metaconfigure', 'PublicPermission'),
                               ('metadirectives', 'IClassDirective'),
                               ('site', 'setSite'),
                               ('vocabulary', 'UtilityTerm'),
                               ('interfaces', 'INewLocalSite')):
        locals()['test_' + mod_name] = _make_import_test(mod_name, attrname)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
