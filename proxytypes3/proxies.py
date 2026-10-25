class AbstractProxy:
    """
    Delegates all operations (except ``.__subject__``) to another object.
    """

    __slots__ = ()

    def __call__(self, *args, **kw):
        return self.__subject__(*args, **kw)

    def __getattribute__(self, attr, oga=object.__getattribute__):
        subject = oga(self, '__subject__')
        if attr == '__subject__':
            return subject
        return getattr(subject, attr)

    def __setattr__(self, attr, val, osa=object.__setattr__):
        if attr == '__subject__':
            osa(self, attr, val)
        else:
            setattr(self.__subject__, attr, val)

    def __delattr__(self, attr, oda=object.__delattr__):
        if attr == '__subject__':
            oda(self, attr)
        else:
            delattr(self.__subject__, attr)

    if hasattr(int, '__nonzero__'):
        def __nonzero__(self):
            return bool(self.__subject__)

    def __getitem__(self, arg):
        return self.__subject__[arg]

    def __setitem__(self, arg, val):
        self.__subject__[arg] = val

    def __delitem__(self, arg):
        del self.__subject__[arg]

    def __getslice__(self, i, j):
        return self.__subject__[i:j]

    def __setslice__(self, i, j, val):
        self.__subject__[i:j] = val

    def __delslice__(self, i, j):
        del self.__subject__[i:j]

    def __contains__(self, ob):
        return ob in self.__subject__

    for name in 'repr str hash len abs complex int long float iter oct hex bool operator.index math.trunc'.split():
        if name in ('len', 'complex') or hasattr(int, f'__{name.split(".")[-1]}__'):
            if '.' in name:
                name = name.split('.')
                exec(f"global {name[1]}; from {name[0]} import {name[1]}")
                name = name[1]
            exec(f"def __{name}__(self): return {name}(self.__subject__)")

    for name in 'cmp', 'coerce', 'divmod':
        if hasattr(int, f'__{name}__'):
            exec(f"def __{name}__(self,ob): return {name}(self.__subject__,ob)")

    for name, op in [
        ('lt', '<'), ('gt', '>'), ('le', '<='), ('ge', '>='),
        ('eq', '=='), ('ne', '!=')
    ]:
        exec(f"def __{name}__(self,ob): return self.__subject__ {op} ob")

    for name, op in [('neg', '-'), ('pos', '+'), ('invert', '~')]:
        exec(f"def __{name}__(self): return {op} self.__subject__")

    for name, op in [
        ('or', '|'), ('and', '&'), ('xor', '^'), ('lshift', '<<'), ('rshift', '>>'),
        ('add', '+'), ('sub', '-'), ('mul', '*'), ('div', '/'), ('mod', '%'),
        ('truediv', '/'), ('floordiv', '//')
    ]:
        if name == 'div' and not hasattr(int, '__div__'):
            continue
        exec((
            f"def __{name}__(self, ob):\n"
            f"    return self.__subject__ {op} ob\n"
            "\n"
            f"def __r{name}__(self, ob):\n"
            f"    return ob {op} self.__subject__\n"
            "\n"
            f"def __i{name}__(self, ob):\n"
            f"    self.__subject__ {op}=ob\n"
            "    return self\n"
        ))

    del name, op

    # Oddball signatures

    def __rdivmod__(self, ob):
        return divmod(ob, self.__subject__)

    def __pow__(self, *args):  # pylint: disable=unexpected-special-method-signature
        # Deliberately variadic: pow(subject), pow(subject, exp), pow(subject, exp, mod).
        return pow(self.__subject__, *args)

    def __ipow__(self, ob):
        self.__subject__ **= ob # pylint: disable=assigning-non-slot
        return self

    def __rpow__(self, ob):
        return pow(ob, self.__subject__)


class ObjectProxy(AbstractProxy):
    """
    Proxy for a specific object.
    """

    __slots__ = ('__subject__',)

    def __init__(self, subject):
        self.__subject__ = subject


class CallbackProxy(AbstractProxy):
    """
    Proxy for a dynamically-chosen object.
    """

    __slots__ = ('__callback__',)

    def __init__(self, func):
        set_callback(self, func)

get_callback = CallbackProxy.__callback__.__get__
set_callback = CallbackProxy.__callback__.__set__
CallbackProxy.__subject__ = property(lambda self, gc=get_callback: gc(self)())


class LazyProxy(CallbackProxy):
    """
    Proxy for a lazily-obtained object, that is cached on first use.
    """
    __slots__ = ('__cache__',)

get_cache = LazyProxy.__cache__.__get__
set_cache = LazyProxy.__cache__.__set__

def __subject__(self, get_cache=get_cache, set_cache=set_cache): # pylint: disable=redefined-outer-name
    try:
        return get_cache(self)
    except AttributeError:
        set_cache(self, get_callback(self)())
        return get_cache(self)

LazyProxy.__subject__ = property(__subject__, set_cache)
del __subject__


class AbstractWrapper(AbstractProxy):
    """
    Mixin to allow extra behaviors and attributes on proxy instance.
    """

    __slots__ = ()

    def __getattribute__(self, attr, oga=object.__getattribute__):
        if attr.startswith('__'):
            subject = oga(self, '__subject__')
            if attr == '__subject__':
                return subject
            return getattr(subject, attr)
        return oga(self, attr)

    def __getattr__(self, attr, oga=object.__getattribute__):
        return getattr(oga(self, '__subject__'), attr)

    def __setattr__(self, attr, val, osa=object.__setattr__):
        if attr == '__subject__' or hasattr(type(self), attr) and not attr.startswith('__'):
            osa(self, attr, val)
        else:
            setattr(self.__subject__, attr, val)

    def __delattr__(self, attr, oda=object.__delattr__):
        if attr == '__subject__' or hasattr(type(self), attr) and not attr.startswith('__'):
            oda(self, attr)
        else:
            delattr(self.__subject__, attr)


class ObjectWrapper(ObjectProxy, AbstractWrapper):
    __slots__ = ()


class CallbackWrapper(CallbackProxy, AbstractWrapper):
    __slots__ = ()


class LazyWrapper(LazyProxy, AbstractWrapper):
    __slots__ = ()
