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


def testingNextUtility(utility, nextutility, interface, name='',
                       service=None, nextservice=None):
    """Provide a next utility for testing.

    Since utilities must be registered in services, we really provide a next
    utility service in which we place the next utility. If you do not pass in
    any services, they will be created for you.

    For a simple usage of this function, see the doc test of
    `queryNextUtility()`. Here is a demonstration that passes in the services
    directly and ensures that the `__parent__` attributes are set correctly.

    First, we need to create a utility interface and implementation:

      >>> from zope.interface import Interface, implements
      >>> class IAnyUtility(Interface):
      ...     pass
      
      >>> class AnyUtility(object):
      ...     implements(IAnyUtility)
      ...     def __init__(self, id):
      ...         self.id = id
      
      >>> any1 = AnyUtility(1)
      >>> any1next = AnyUtility(2)

    Now we create a special utility service that can have a location:

      >>> UtilityService = type('UtilityService', (GlobalUtilityService,),
      ...                       {'__parent__': None})

    Let's now create one utility service

      >>> utils = UtilityService()

    and pass it in as the original utility service to the function:

      >>> testingNextUtility(any1, any1next, IAnyUtility, service=utils)
      >>> any1.__parent__ is utils
      True
      >>> utilsnext = any1next.__parent__
      >>> utils.__parent__.next.data['Utilities'] is utilsnext
      True

    or if we pass the current and the next utility service:

      >>> utils = UtilityService()
      >>> utilsnext = UtilityService()
      >>> testingNextUtility(any1, any1next, IAnyUtility,
      ...                    service=utils, nextservice=utilsnext)
      >>> any1.__parent__ is utils
      True
      >>> any1next.__parent__ is utilsnext
      True
    
    """
    UtilityService = type('UtilityService', (GlobalUtilityService,),
                          {'__parent__': None})
    if service is None:
        service = UtilityService()
    if nextservice is None:
        nextservice = UtilityService()
    from zope.app.component.localservice import testingNextService
    testingNextService(service, nextservice, zapi.servicenames.Utilities)

    service.provideUtility(interface, utility, name)
    utility.__parent__ = service
    nextservice.provideUtility(interface, nextutility, name)
    nextutility.__parent__ = nextservice
