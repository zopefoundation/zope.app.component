import os

from setuptools import setup, find_packages, Extension

setup(name='zope.app.component',
      version = '3.4.0b3',
      url='http://pypi.zope.org/pypi/zope.app.component',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',

      packages=find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages=['zope', 'zope.app'],
      extras_require=dict(test=['zope.app.testing',
                                'zope.app.securitypolicy',
                                'zope.app.zcmlfiles',
                                'zope.modulealias',
                                'zope.app.schema',
                                'zope.testbrowser',
                                ],
                          back35=['zope.app.layers']),
      include_package_data = True,
      install_requires=['setuptools',
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
      zip_safe = False,
      )

