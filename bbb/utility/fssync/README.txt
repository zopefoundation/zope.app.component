This package is pretty slim, containing only configuration data for
the application server.  This is maintained as a Python package to
allow future versions to speciallize the registered fssync adapter
implementation and allow existing instances to be used with the
updated software.  Using the ZCML slug allows software-related
configuration changes to be made in a way that's compatible with
existing instance homes; placing the configuration directly in the
instance home's site-packages/ would prevent existing site from
picking up bug fixes that are effected by or otherwise involve
configuration changes.
