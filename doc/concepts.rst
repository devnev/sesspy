
Concepts
========

A primary concept is that of a :dfn:`session factory`. A session factory is a
callable that returns a thread‐local :class:`.Session` object. Examples of
session factories include:

- the :class:`.SessionFactory` class
- the :class:`.ComponentRef` class

The resulting :class:`.Session` object is, as mentioned, thread‐local. The
existence of a ``Session`` object does not imply that a session has been
opened.  To access a session for the target resource, the :meth:`.Session.open`
method must be called, and will return an object for the session. Committing or
aborting the session must also be done via the ``Session`` object. The
``Session`` object can also be used as a guard in a with statement.

A :dfn:`source` is any object capable of opening sessions or connections, i.e. an
interface to resources. To convert a source into a format useable by sesspy,
various helpers can be found with the :mod:`.source` module. In particular,
:class:`.SourceAdapter` (and its wrappers :func:`.source_adapter_factory` and
:func:`.sessionless_source_adapter`) can be used to supply ``open``, ``commit``
and ``abort`` methods used by sesspy.

