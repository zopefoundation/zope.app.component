

def install():

    import sys
    import localservice

    sys.modules['zope.app.component.localservice'] = localservice
