# -*- coding: utf-8 -*-
from __future__ import absolute_import

class ResolveError(ValueError):
    pass

class ComponentError(Exception):
    pass

class ComponentRef(object):
    def __init__(self, ref, obj, reg=None):
        self.ref = ref
        self.obj = obj
        if reg is None:
            from .registry import default_registry
            reg = default_registry
        self.reg = reg

    def copy(self, **kwargs):
        kwargs.setdefault('ref', self.ref)
        kwargs.setdefault('obj', self.obj)
        kwargs.setdefault('reg', self.reg)
        return ComponentRef(**kwargs)

    @property
    def dictkey(self):
        return '_%s__%s__%s' % (
            __name__.replace('.', '__'),
            self.__class__.__name__,
            id(self),
        )

    def __get__(self, obj, type=None):
        if obj is not None:
            try:
                d = obj.__dict__
            except AttributeError:
                pass
            else:
                return d.get(self.dictkey)
        return self

    def __set__(self, obj, ref):
        if obj is None:
            self.ref = ref
        else:
            obj.__dict__[self.dictkey] = self.copy(ref=ref, obj=obj)

    def resolve(self, obj=None):
        if obj is not None and obj is not self.obj:
            return self.__get__(obj).resolve()

        if hasattr(self.ref, 'local_context'):
            resolved = self.ref
        elif isinstance(self.ref, basestring) and '.' in self.ref:
            _imp, _from = self.ref.rsplit('.', 1)
            _temp = __import__(_imp, fromlist=[_from])
            resolved = getattr(_temp, _from)
        elif isinstance(self.ref, basestring) and self.reg is not None:
            resolved = self.reg[self.ref]
            if hasattr(resolved, 'resolve'):
                resolved = resolved.resolve()
        else:
            resolved = None

        if not hasattr(resolved, 'local_context'):
            raise ResolveError("Component ref %r does not resolve to component config" % self.ref)
        self.ref = resolved

        return resolved

    def __call__(self):
        return self.resolve().local_context()

class LocalContext(object):
    def __init__(self, instance_opener):
        self.instance_opener = instance_opener
        self.instance = None

    def __enter__(self):
        self.instance = self.instance_opener.open()
        return self.instance

    def __exit__(self, exc, type, tb):
        if exc is None:
            self.instance_opener.commit(self.instance)
        else:
            self.instance_opener.abort(self.instance)

class ComponentConfig(object):
    def __init__(self, component=None, global_opener=None,
                 global_opener_factory=None,
                 local_opener_factory=None):
        self.component = component
        self.global_opener = global_opener
        self.global_opener_factory = global_opener_factory
        self.local_opener_factory = local_opener_factory
        from .local import Local
        self.locals = Local()

    def local_context(self):
        if self.global_opener is None and self.global_opener_factory is not None:
            if self.component is not None:
                self.global_opener = self.global_opener_factory(self.component)
            else:
                self.global_opener = self.global_opener_factory()

        opener = getattr(self.locals.opener, None)
        if opener is None and self.local_opener_factory is not None:
            if self.global_opener is not None:
                opener = self.local_opener_factory(self.global_opener)
            if self.component is not None:
                opener = self.local_opener_factory(self.component)
            else:
                opener = self.local_opener_factory()
            self.locals.opener = opener
        if opener is None and self.global_opener is not None:
            self.opener = self.global_opener
        if opener is None and self.component is not None:
            from .openers import SingletonOpener
            opener = SingletonOpener(self.component)
        if opener is None:
            raise ComponentError("Unable to create context for %r" % self)

        return LocalContext(self.opener)
