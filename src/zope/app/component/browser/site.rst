Managing a Site
---------------


Create the browser object we'll be using.

    >>> from zope.testbrowser.wsgi import Browser
    >>> browser = Browser()
    >>> browser.handleErrors = False
    >>> browser.addHeader("Authorization", "Basic mgr:mgrpw")
    >>> browser.addHeader("Accept-Language", "en-US")

    >>> browser.open('http://localhost/manage')

When we originally enter a Zope instance, there is only a root folder that is
already a site:

    >>> 'Manage Site' in browser.contents
    True

Let's now add a new folder called ``samplesite`` and make it a site:

    >>> browser.getLink(url='folder.Folder').click()
    >>> browser.getControl(name='new_value').value = 'samplesite'
    >>> browser.getControl('Apply').click()

    >>> browser.getLink('samplesite').click()
    >>> browser.getLink('Make a site').click()

We are automatically forwarded to the site manager of the site. The default
site management folder is always available and initially empty:

    >>> 'default' in browser.contents
    True

    >>> browser.getLink(url="@@registrations.html").click()
    >>> 'Nothing is registered for this site' in browser.contents
    True


We can add registrations to it:

    >>> browser.open("/samplesite/@@addRegistration.html")
    >>> browser.getControl(name="field.provided").value = 'zope.site.interfaces.IFolder'
    >>> browser.getControl(name="field.name").value = "A Folder"
    >>> browser.getControl(name="field.comment").value = "My comment"
    >>> browser.getControl(name="field.actions.register").click()
    >>> 'This object is registered' in browser.contents and 'A Folder' in browser.contents
    True
    >>> 'My comment' in browser.contents
    True


We can view those registrations:

    >>> browser.open("/samplesite/++etc++site/@@registrations.html")
    >>> 'Registrations for this site' in browser.contents and 'A Folder' in browser.contents
    True

We can also delete those registrations:

    >>> browser.getControl(name="ids:list").value = True
    >>> browser.getControl(name="deactivate").click()
    >>> 'Nothing is registered for this site' in browser.contents
    True

Names are optional:

    >>> browser.open("/samplesite/@@addRegistration.html")
    >>> browser.getControl(name="field.provided").value = 'zope.site.interfaces.IFolder'
    >>> browser.getControl(name="field.comment").value = "No Name"
    >>> browser.getControl(name="field.actions.register").click()
    >>> 'This object is registered' in browser.contents and 'No Name' in browser.contents
    True

There's another more limited way to add objects to the site management folder:

    >>> browser.open('/samplesite/++etc++site/default/@@+/index.html')
    >>> browser.getControl(name='type_name').value = "BrowserAdd__zope.app.component.browser.tests.Sample"
    >>> browser.getControl(name="add").click()
    >>> 'samplesite/++etc++site/default/Sample/' in browser.contents
    True

    >>> browser.open('/samplesite/++etc++site/default/@@=/index.html')
    >>> browser.getControl(name='type_name').value = "BrowserAdd__zope.app.component.browser.tests.Sample"
    >>> browser.getControl(name="add").click()
    >>> '@@addRegistration.html' in browser.contents
    True

For testing, we've defined a way that filters to prevent creating objects:

    >>> browser.open('/samplesite/++etc++site/default/@@-/index.html')
    >>> browser.getControl(name='type_name').value = "BrowserAdd__zope.app.component.browser.tests.Sample"
    >>> browser.getControl(name="add").click()
    >>> "This object isn't yet registered" in browser.contents
    True

Let's now delete the site again:

    >>> browser.getLink('[top]').click()
    >>> browser.getControl(name='ids:list').getControl(
    ...     value='samplesite').selected = True

    >>> browser.handleErrors = False
    >>> browser.getControl('Delete').click()

The site should be gone now.

    >>> 'samplesite' in browser.contents
    False
