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
"""Base Mix-in class for Placeful Setups 

$Id$
"""
from zope.app import zapi
from zope.app.testing import setup
from zope.app.testing.placelesssetup import PlacelessSetup
from zope.app.folder import rootFolder

class Place(object):

    def __init__(self, path):
        self.path = path

    def __get__(self, inst, cls=None):
        if inst is None:
            return self

        try:
            # Use __dict__ directly to avoid infinite recursion
            root = inst.__dict__['rootFolder']
        except KeyError:
            root = inst.rootFolder = setup.buildSampleFolderTree()

        return zapi.traverse(root, self.path)

class PlacefulSetup(PlacelessSetup):

    # Places :)
    rootFolder  = Place('')

    folder1     = Place('folder1')
    folder1_1   = Place('folder1/folder1_1')
    folder1_1_1 = Place('folder1/folder1_1/folder1_1_1')
    folder1_1_2 = Place('folder1/folder1_2/folder1_1_2')
    folder1_2   = Place('folder1/folder1_2')
    folder1_2_1 = Place('folder1/folder1_2/folder1_2_1')

    folder2     = Place('folder2')
    folder2_1   = Place('folder2/folder2_1')
    folder2_1_1 = Place('folder2/folder2_1/folder2_1_1')


    def setUp(self, folders=False, site=False):
        setup.placefulSetUp()
        if folders or site:
            return self.buildFolders(site)

    def tearDown(self):
        setup.placefulTearDown()
        # clean up folders and placeful service managers and services too?

    def buildFolders(self, site=False):
        self.rootFolder = setup.buildSampleFolderTree()
        if site:
            return self.makeSite()

    def makeSite(self, path='/'):
        folder = zapi.traverse(self.rootFolder, path)
        return setup.createServiceManager(folder, True)

    def createRootFolder(self):
        self.rootFolder = rootFolder()

    def createStandardServices(self):
        '''Create a bunch of standard placeful services'''

        setup.createStandardServices(self.rootFolder)
