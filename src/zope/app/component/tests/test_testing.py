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

import unittest

from zope.component.interfaces import ISite

from zope.app.component import testing


class TestTesting(testing.PlacefulSetup,
                  unittest.TestCase):

    def setUp(self):
        super().setUp(site=True)

    def test_is_site(self):
        self.assertTrue(ISite.providedBy(self.rootFolder))

    def test_build_sample_folder(self):
        # We don't actually test the details of the layout, just some basics
        tree1 = testing.buildSampleFolderTree()
        self.assertIsNotNone(tree1)
        self.assertIsNot(tree1, testing.buildSampleFolderTree())
        self.assertIn('folder1', tree1)

    def test_new_root(self):
        cur_root = self.rootFolder
        self.createRootFolder()
        self.assertIsNot(self.rootFolder, cur_root)

    def test_place_rebuilds_root(self):
        f1 = self.folder1
        del self.rootFolder
        f2 = self.folder1
        self.assertIsNot(f1, f2)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
