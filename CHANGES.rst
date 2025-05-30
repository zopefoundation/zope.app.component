=======
CHANGES
=======

5.1 (unreleased)
----------------

- Add support for Python 3.12, 3.13.

- Drop support for Python 3.7, 3.8.


5.0 (2023-02-21)
----------------

- Add support for Python 3.8, 3.9, 3.10, 3.11.

- Drop support for Python 2.7, 3.4, 3.5, 3.6.

- Remove deprecated:

    - ``zope.app.component.getNextUtility`` (import from ``zope.site``)
    - ``zope.app.component.queryNextUtility`` (import from ``zope.site``)
    - ``zope.app.component.getNextSiteManager`` (no replacement)
    - ``zope.app.component.queryNextSiteManager`` (no replacement)


4.1.0 (2018-10-22)
------------------

- Add support for Python 3.7.


4.0.0 (2017-05-02)
------------------

- Remove test dependencies on zope.app.testing, zope.app.zcmlfiles,
  and others.

- Remove install dependency on zope.app.form, replaced with direct
  imports of zope.formlib.

- Simplify ``zope.app.component.testing`` to remove the deprecated or
  broken functionality in ``testingNextUtility`` and
  ``SiteManagerStub``. ``PlacefulSetup`` is retained (and incorporates
  much of what was previously inherited from ``zope.app.testing``),
  although use of ``zope.component.testing.PlacelessSetup`` is
  suggested when possible.

- Add support for PyPy and Python 3.4, 3.5 and 3.6.


3.9.3 (2011-07-27)
------------------

- Replaced an undeclared test dependency on ``zope.app.authentication`` with
  ``zope.password``.

- Removed unneeded dependencies.


3.9.2 (2010-09-17)
------------------

- Replaced a testing dependency on ``zope.app.securitypolicy`` with one on
  ``zope.securitypolicy``.


3.9.1 (2010-09-01)
------------------

- No longer using deprecated ``zope.testing.doctest``. Use python's build-in
  ``doctest`` instead.

- Replaced the dependency on ``zope.deferredimport`` with BBB imports.


3.9.0 (2010-07-19)
------------------

- Added missing BBB import in ``zope.app.component.metaconfigure``.

- Requiring at least ``zope.component`` 3.8 where some modules have
  moved which are BBB imported here.


3.8.4 (2010-01-08)
------------------

- Import hooks functionality from zope.component after it was moved there from
  zope.site.

- Import ISite and IPossibleSite from zope.component after they were moved
  there from zope.location. This lifts the direct dependency on zope.location.

- Fix tests using a newer zope.publisher that requires zope.login.

3.8.3 (2009-07-11)
------------------

- Removed unnecessary dependency on ``zope.app.interface``.


3.8.2 (2009-05-22)
------------------

- Fix missing import in ``zope.app.component.metadirectives``.


3.8.1 (2009-05-21)
------------------

- Add deprecation note.

3.8.0 (2009-05-21)
------------------

- IMPORTANT: this package is now empty except for some ZMI definitions
  in zope.app.component.browser. Functionality from this package has
  been moved to ``zope.site``, ``zope.componentvocabulary`` and
  ``zope.component``, so preferably import from those locations.

- zope.componentvocabulary has the vocabulary implementations that
  were in zope.app.componentvocabulary now, import them from there for
  backwards compatibility.

- moved zope:resource and zope:view directive implementation and tests
  over into zope.component [zcml].

3.7.0 (2009-04-01)
------------------

- Removed deprecated `zope:defaultView` directive and its
  implementation.  New directive to set default view is
  `browser:defaultView`.

3.6.1 (2009-03-12)
------------------

- Make ``class`` directive schemas importable from old location,
  raising a deprecation warning. It was moved in the previous release,
  but some custom directives could possibly use its schemas.

- Deprecate import of ClassDirective to announce about new location.

- Change package's mailing list address to zope-dev at zope.org,
  because zope3-dev at zope.org is now retired.

- Adapt to the move of IDefaultViewName from zope.component.interfaces
  to zope.publisher.interfaces.

3.6.0 (2009-01-31)
------------------

- Moved the implementation of the <class> directive from this package to
  `zope.security`.  In particular, the module
  `zope.app.component.contentdirective` has moved to
  `zope.security.metaconfigure`, and a compatibility import has been
  left in its place.

- Extracted `zope.site` from zope.app.component with backwards
  compatibility imports in place. Local site related functionality
  is now in `zope.site` and packages should import from there.

- Remove more deprecated on 3.5 code:

  * zope.app.component.fields module that was pointing to the
    removed back35's LayerField.
  * zope.app.component.interface module that was moved to
    zope.component.interface ages ago.
  * zope:content and zope:localUtility directives.
  * zope:factory directive.
  * deprecated imports in zope.component.metaconfigure
  * browser:tool directive and all zope.component.browser
    meta.zcml stuff.

- Remove "back35" extras_require as it doesn't make
  any sense now.

- Remove zope.modulealias test dependency as it is
  not used anywhere.

- Deprecate ISite and IPossibleSite imports from
  zope.app.component.interfaces. They were moved
  to zope.location.interfaces ages ago. Fix imports
  in zope.app.component itself.

3.5.0 (2008-10-13)
------------------

- Remove deprecated code slated for removal on 3.5.

3.4.1 (2007-10-31)
------------------

- Resolve ``ZopeSecurityPolicy`` deprecation warning.


3.4.0 (2007-10-11)
------------------

- Initial release independent of the main Zope tree.
