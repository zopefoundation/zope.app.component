============
Registration
============

:Author: Jim Fulton
:Version: $Rev$

Many services act as component registries.  Their primary job is to
allow components to be looked up based on parameters such as names,
interfaces or both. Examples of component registries include the
adapter service, the presentation service, the service service, and the
utility service.

An important feature of component registration services is that they
support multiple conflicting registrations for the same registration
parameters.  At most one of the conflicting registrations is active.
A site developer can switch between alternate components by simply
changing which one is active.

Consider the following scenario.  A product provides a utility.  A
site manager gets a new version of the utility and installs
it.  The new version is active.  The site developer then finds a
bug in the new version.  Because the old utility is still registered,
the site developer can easily switch back to it by making it active.
In fact, the site manager only needs to inactivate the new version and
the old version becomes active again.

To support this registration flexibility, Zope provides a registration
framework:

- Registration objects manage registration parameters and other data.
  They also provide access to registered components. In some cases,
  such as adapters and views, they are responsible for constructing
  components on the fly.

- Registration managers support management of registration objects
  in folders.  Each folder has a registration manager containing all
  of the registration objects for that folder.

- `RegistrationStack` objects manage multiple registrations for
  the same registration parameters (at most one of which is active at
  any given time).  For example, in the case of a utility service
  these would be registrations for the same interface and name.

There are two kinds of registrations:

- Local-object registrations register objects in site-management
  folders, such as service instances, utility instances, database
  connections, caches, and templates.

  Local objects are named using a path.

  Local-object registrations are primarily managed through the objects
  that they register. The objects have a "Registrations" tab that
  allows the registrations (usually 1) for the objects to be managed.

  Local-object registrations can also be browsed and edited in the
  registration manager for the folder containing the registered
  components.

- Module-global registrations register objects stored in
  modules. Objects in modules aren't managable directly, so we can't
  manage their registrations through them.  (The state of an object
  stored in a module must be represented solely by the module source.)

  Module-global objects are named using dotted names.

  Module-global registrations are added, browsed and edited in
  registration mananagers.

Implementation of services that support registration is substantially
more difficult that implementation of non-registry services.

High-level registration concepts glossary
-----------------------------------------

There are several major concepts/terms that need to be understood

Registerables
  Registerables are objects that can be registered.  They implement the
  `IRegisterable` interface.

Registries
  Registeries are objects that registerables are registered with.
  Typically, these are component-management services like the adapter
  or utility service.

Registration objects
  Registration objects store data about registrations.  They store
  registration data and represent the relationship between registries
  and registerables.

Registration managers
  Registration managers are containers for managing registrations.
  Registrations are stored in registration managers.  All of the
  registrations for objects stored in a site-management folder are
  contained in the folder's registration manager. Currently, the
  registration manager is an item in the folder. We want to change
  this so that the registration manager is exposed as a folder tab
  rather than as an item.

Registration stack
  Registries allow multiple registrations for the same set of
  registration parameters. At most one registration for a set of
  parameters can be active at one time, but multiple registrations are
  managed. 

  Registries provide functions for looking up (`queryRegistrationsFor()`)
  or creating (`createRegistrationsFor()`) registration stacks.  These
  methods are passed registration objects whos attribute values are
  used to specify the desired registration stacks.

  This is a little but confusing, so we'll look at an example.
  Utilities are registered using 2 parameterer, the interface provided
  by the uttility, and the utility name.  For a given interface and
  name, the utility service may have multiple utility
  registrations. It uses a registration stack to store these. We can
  get the registration stack by calling `queryRegistrationsFor()` with
  a registration object that has the desired interface and name.  The
  registration object passed need not be in in the stack. It is used
  soley to provide the parameters.  

Registered
  The interface `IRegistered` provides storage and access to the
  registrations for a registerable.  When we make a registration, we
  refer to it in a registration stack and in the registered object.
