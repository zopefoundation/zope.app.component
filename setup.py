##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
# This package is developed by the Zope Toolkit project, documented here:
# https://zopetoolkit.readthedocs.io/
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""Setup for zope.app.component package
"""
import os

from setuptools import setup


def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()


test_requires = [
    'zope.app.appsetup',
    'zope.app.basicskin >= 4.0',
    'zope.app.container[test] >= 4.0',
    'zope.app.content',
    'zope.app.dependable >= 4.0',
    'zope.app.http',
    'zope.app.pagetemplate >= 4.0',
    'zope.app.principalannotation',
    'zope.app.publication',
    'zope.app.publisher',
    'zope.app.rotterdam >= 4.0',
    'zope.app.schema',
    'zope.app.testing',
    'zope.app.wsgi',

    'zope.applicationcontrol',
    'zope.browser',
    'zope.browserresource',
    'zope.copypastemove',
    'zope.login',
    'zope.password',
    'zope.principalannotation',
    'zope.principalregistry',
    'zope.proxy >= 4.2.1',
    'zope.securitypolicy',
    'zope.site',
    'zope.testbrowser >= 5.2',
    'zope.testing',
    'zope.testrunner >= 6.4',
]

setup(name='zope.app.component',
      version='6.0',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.dev',
      description='Local Zope Component Support',
      long_description=(
          read('README.rst')
          + '\n\n.. contents:: \n\n' +
          read('CHANGES.rst')
      ),
      keywords="zope component architecture local",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Programming Language :: Python :: 3.13',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope :: 3',
      ],
      url='https://github.com/zopefoundation/zope.app.component',
      license='ZPL-2.1',
      python_requires='>=3.9',
      extras_require={
          'test': test_requires,
      },
      install_requires=[
          'setuptools',
          'zope.site',
          'zope.app.container >= 4.0',
          'zope.app.pagetemplate >= 4.0',
          'zope.component[hook,zcml] >= 4.3.0',
          'zope.deprecation',
          'zope.exceptions',
          'zope.formlib',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.publisher >= 4.3.1',
          'zope.schema',
          'zope.security',
          'zope.traversing',
          'zope.componentvocabulary',
      ],
      include_package_data=True,
      zip_safe=False,
      )
