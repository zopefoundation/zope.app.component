"""Filesystem synchronization support for zope.app.site.

$Id$
"""
from zope.fssync.server.entryadapter import AttrMapping, DirectoryAdapter
from zope.proxy import removeAllProxies


_smattrs = (
    '_modules',                         # PersistentModuleRegistry
    '_bindings',
)

class ServiceManagerAdapter(DirectoryAdapter):

    def extra(self):
        obj = removeAllProxies(self.context)
        return AttrMapping(obj, _smattrs)
