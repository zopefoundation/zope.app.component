##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Setup for zope.app.catalog package

$Id: setup.py 80209 2007-09-27 09:38:31Z berndroessl $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.component',
      version = '3.5.0',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='Local Zope Component Support',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Documentation\n'
          '**********************\n'
          + '\n\n' +
          read('src', 'zope', 'app', 'component', 'README.txt')
          + '\n\n' +
          read('src', 'zope', 'app', 'component', 'site.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope component architecture local",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://pypi.python.org/pypi/zope.app.component',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require=dict(
          test=['zope.app.testing',
                'zope.app.securitypolicy',
                'zope.app.zcmlfiles',
                'zope.modulealias',
                'zope.app.schema',
                'zope.testbrowser',
                ],
          back35=['zope.app.layers']),
      install_requires=[
          'setuptools',
          'zope.annotation',
          'zope.app.container',
          'zope.app.interface',
          'zope.app.pagetemplate',
          'zope.app.security',
          'zope.cachedescriptors',
          'zope.component [hook]',
          'zope.configuration',
          'zope.deferredimport',
          'zope.deprecation',
          'zope.event',
          'zope.exceptions',
          'zope.filerepresentation',
          'zope.formlib',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.lifecycleevent',
          'zope.location>3.4.0b1',
          'zope.publisher',
          'zope.schema',
          'zope.security',
          'zope.thread',
          'zope.traversing',
          'ZODB3',
          ],
      include_package_data = True,
      zip_safe = False,
      )

