##############################################################################
#
# Copyright (c) 2001-2007 Zope Foundation and Contributors.
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
"""
Test helpers.

This is part of the public API of this package.
"""

from zope.component.hooks import setSite
from zope.component.interfaces import ISite
from zope.component.testing import PlacelessSetup
from zope.container.interfaces import ISimpleReadContainer
from zope.container.traversal import ContainerTraversable
from zope.site.folder import Folder
from zope.site.folder import rootFolder
from zope.site.site import LocalSiteManager
from zope.traversing.api import traverse
from zope.traversing.interfaces import ITraversable

from zope import component


def buildSampleFolderTree():
    r"""
    Create a tree of folders and return the root::

           ____________ rootFolder ______________________________
          /                                    \                 \
       folder1 __________________            folder2           folder3
         |                       \             |                 |
       folder1_1 ____           folder1_2    folder2_1         folder3_1
         |           \            |            |
       folder1_1_1 folder1_1_2  folder1_2_1  folder2_1_1
    """

    root = rootFolder()
    root['folder1'] = Folder()
    root['folder1']['folder1_1'] = Folder()
    root['folder1']['folder1_1']['folder1_1_1'] = Folder()
    root['folder1']['folder1_1']['folder1_1_2'] = Folder()
    root['folder1']['folder1_2'] = Folder()
    root['folder1']['folder1_2']['folder1_2_1'] = Folder()
    root['folder2'] = Folder()
    root['folder2']['folder2_1'] = Folder()
    root['folder2']['folder2_1']['folder2_1_1'] = Folder()
    root["\N{CYRILLIC SMALL LETTER PE}"
         "\N{CYRILLIC SMALL LETTER A}"
         "\N{CYRILLIC SMALL LETTER PE}"
         "\N{CYRILLIC SMALL LETTER KA}"
         "\N{CYRILLIC SMALL LETTER A}3"] = Folder()
    root["\N{CYRILLIC SMALL LETTER PE}"
         "\N{CYRILLIC SMALL LETTER A}"
         "\N{CYRILLIC SMALL LETTER PE}"
         "\N{CYRILLIC SMALL LETTER KA}"
         "\N{CYRILLIC SMALL LETTER A}3"][
        "\N{CYRILLIC SMALL LETTER PE}"
        "\N{CYRILLIC SMALL LETTER A}"
        "\N{CYRILLIC SMALL LETTER PE}"
        "\N{CYRILLIC SMALL LETTER KA}"
        "\N{CYRILLIC SMALL LETTER A}3_1"] = Folder()

    return root


def createSiteManager(folder, setsite=False):
    "Make the given folder a site, and optionally make it the current site."
    if not ISite.providedBy(folder):
        folder.setSiteManager(LocalSiteManager(folder))
    if setsite:
        setSite(folder)
    return traverse(folder, "++etc++site")


def setUpTraversal():
    "Make simple read containers traversable."
    from zope.traversing.testing import setUp
    setUp()
    component.provideAdapter(ContainerTraversable,
                             (ISimpleReadContainer,),
                             ITraversable)


class Place:
    """A property-like descriptor that traverses its name starting from

    rootFolder.
    """

    def __init__(self, path):
        self.path = path

    def __get__(self, inst, cls=None):
        if inst is None:  # pragma: no cover
            return self

        try:
            # Use __dict__ directly to avoid infinite recursion
            root = inst.__dict__['rootFolder']
        except KeyError:
            root = inst.rootFolder = buildSampleFolderTree()

        return traverse(root, self.path)


class PlacefulSetup(PlacelessSetup):
    """
    A unittest fixture that optionally creates many folders and a site.

    In many cases, :class:`zope.component.testing.PlacelessSetup` is
    sufficient.
    """

    # Places :)
    rootFolder = Place('')

    folder1 = Place('folder1')
    folder1_1 = Place('folder1/folder1_1')
    folder1_1_1 = Place('folder1/folder1_1/folder1_1_1')
    folder1_1_2 = Place('folder1/folder1_2/folder1_1_2')
    folder1_2 = Place('folder1/folder1_2')
    folder1_2_1 = Place('folder1/folder1_2/folder1_2_1')

    folder2 = Place('folder2')
    folder2_1 = Place('folder2/folder2_1')
    folder2_1_1 = Place('folder2/folder2_1/folder2_1_1')

    folder3 = Place("\N{CYRILLIC SMALL LETTER PE}"
                    "\N{CYRILLIC SMALL LETTER A}"
                    "\N{CYRILLIC SMALL LETTER PE}"
                    "\N{CYRILLIC SMALL LETTER KA}"
                    "\N{CYRILLIC SMALL LETTER A}3")
    folder3_1 = Place("\N{CYRILLIC SMALL LETTER PE}"
                      "\N{CYRILLIC SMALL LETTER A}"
                      "\N{CYRILLIC SMALL LETTER PE}"
                      "\N{CYRILLIC SMALL LETTER KA}"
                      "\N{CYRILLIC SMALL LETTER A}3/"
                      "\N{CYRILLIC SMALL LETTER PE}"
                      "\N{CYRILLIC SMALL LETTER A}"
                      "\N{CYRILLIC SMALL LETTER PE}"
                      "\N{CYRILLIC SMALL LETTER KA}"
                      "\N{CYRILLIC SMALL LETTER A}3_1")

    def setUp(self, folders=False, site=False):
        PlacelessSetup.setUp(self)
        setUpTraversal()
        if folders or site:
            return self.buildFolders(site)

    def buildFolders(self, site=False):
        self.rootFolder = buildSampleFolderTree()
        if site:
            return self.makeSite()

    def makeSite(self, path='/'):
        folder = traverse(self.rootFolder, path)
        return createSiteManager(folder, True)

    def createRootFolder(self):
        self.rootFolder = rootFolder()
