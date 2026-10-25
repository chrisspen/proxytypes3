import doctest
import unittest
from collections import UserList

from proxytypes3 import *

# pylint: disable=multiple-statements

# Python 2 compatibility shims.
long = int # pylint: disable=redefined-builtin
def cmp(a, b): # pylint: disable=redefined-builtin
    return (a > b) - (a < b)

class ProxyTestMixin:

    def checkInteger(self, v):
        p = self.proxied(v)
        self.assertEqual(p|0x10101, v|0x10101)
        self.assertEqual(p&0x10101, v&0x10101)
        self.assertEqual(p^0x10101, v^0x10101)
        self.assertEqual(~p, ~v)
        self.assertEqual(p << 3, v << 3)
        self.assertEqual(p >> 2, v >> 2)

        self.assertEqual(0x10101|p, 0x10101|v)
        self.assertEqual(0x10101&p, 0x10101&v)
        self.assertEqual(0x10101^p, 0x10101^v)
        self.assertEqual(3 << p, 3 << v)
        self.assertEqual(2 >> p, 2 >> v)
        for f in hex, oct:
            self.assertEqual(f(p), f(v))

        self.checkNumeric(v)

    def checkNumeric(self, v):
        p = self.proxied(v)
        self.assertEqual(p*2, v*2)
        self.assertEqual(2*p, 2*v)
        self.assertEqual(2**p, 2**v)
        self.assertEqual(p**2, v**2)
        self.assertEqual(-p, -v)
        self.assertEqual(+p, +v)
        for f in abs, int, long, float, hash, complex:
            self.assertEqual(f(p), f(v))

        self.assertEqual(p < 22, v < 22)
        self.assertEqual(p >= 10, v >= 10)
        self.assertEqual(p > 9.0, v > 9.0)
        self.assertEqual(p <= 9.25, v <= 9.25)
        self.assertEqual(p == 7, v == 7)
        self.assertEqual(p != 18, v != 18)

        self.assertEqual(16 + p, 16 + v)
        self.assertEqual(62 - p, 62 - v)
        self.assertEqual(p + 16, v + 16)
        self.assertEqual(p - 62, v - 62)
        self.assertEqual(p % 7, v % 7)
        self.assertEqual(p / 6, v / 6)

        self.assertEqual(22 < p, 22 < v)
        self.assertEqual(10 >= p, 10 >= v)
        self.assertEqual(9.0 > p, 9.0 > v)
        self.assertEqual(9.25 <= p, 9.25 <= v)
        self.assertEqual(7 == p, 7 == v)
        self.assertEqual(18 != p, 18 != v)

        self.assertEqual(cmp(p, 14), cmp(v, 14))
        self.assertEqual(cmp(14, p), cmp(14, v))

        self.assertEqual(divmod(p, 3), divmod(v, 3))

        if v:
            self.assertEqual(divmod(3, p), divmod(3, v))
            self.assertEqual(62//p, 62//v)
            self.assertEqual(7/p, 7/v)
            self.assertEqual(7%p, 7%v)

        self.checkBasics(v)

    def checkList(self, v):
        p = self.proxied(v)
        for i in range(len(v)): # pylint: disable=consider-using-enumerate
            self.assertEqual(p[i], v[i])
            self.assertEqual(p[i:], v[i:])
            self.assertEqual(p[:i], v[:i])
            self.assertEqual(p[i::-1], v[i::-1])
        self.checkContainer(v)

        c = list(v)
        del p[::1]
        del c[::1]
        self.assertEqual(v, c)

        p[1:1] = [23]
        c[1:1] = [23]
        self.assertEqual(v, c)

    def checkContainer(self, v):
        p = self.proxied(v)
        self.assertEqual(list(p), list(v))
        self.assertEqual(list(iter(p)), list(iter(v)))
        self.assertEqual(len(p), len(v))
        self.assertEqual(42 in p, 42 in v)
        self.assertEqual(99 in p, 99 in v)
        self.checkBasics(v)

    def checkBasics(self, v):
        p = self.proxied(v)
        for f in bool, repr, str:
            self.assertEqual(f(p), f(v))

    def testNumbers(self):
        for i in range(20):
            self.checkInteger(i)

        f = -40
        while f <= 20.0:
            self.checkNumeric(f)
            f += 2.25

    def testLists(self):
        for d in [1, 2], [3, 42, 59], [99, 23, 55]:
            self.checkList(d)
            self.checkList(UserList(d))


class InPlaceMixin(ProxyTestMixin):

    def checkInteger(self, v):
        def mk():
            return (self.proxied(v), v)
        p, v = mk(); p |= 0x10101; v |= 0x10101; self.assertEqual(p.__subject__, v)
        p, v = mk(); p &= 0x10101; v &= 0x10101; self.assertEqual(p.__subject__, v)
        p, v = mk(); p ^= 0x10101; v ^= 0x10101; self.assertEqual(p.__subject__, v)
        p, v = mk(); p <<= 3; v <<= 3; self.assertEqual(p.__subject__, v)
        p, v = mk(); p >>= 3; v >>= 3; self.assertEqual(p.__subject__, v)
        ProxyTestMixin.checkInteger(self, v)

    def checkNumeric(self, v):
        def mk():
            return (self.proxied(v), v)
        p, v = mk(); p += 17; v += 17; self.assertEqual(p.__subject__, v)
        p, v = mk(); p -= 22; v -= 22; self.assertEqual(p.__subject__, v)
        p, v = mk(); p *= 15; v *= 15; self.assertEqual(p.__subject__, v)
        p, v = mk(); p //= 3; v //= 3; self.assertEqual(p.__subject__, v)
        p, v = mk(); p **= 2; v **= 2; self.assertEqual(p.__subject__, v)
        p, v = mk(); p /= 61; v /= 61; self.assertEqual(p.__subject__, v)
        p, v = mk(); p %= 19; v %= 19; self.assertEqual(p.__subject__, v)
        ProxyTestMixin.checkNumeric(self, v)


class TestCallbackProxy(ProxyTestMixin, unittest.TestCase):

    def proxied(self, v):
        return CallbackProxy(lambda: v)

class TestObjectProxy(InPlaceMixin, unittest.TestCase):
    proxied = ObjectProxy

class TestLazyProxy(InPlaceMixin, unittest.TestCase):

    def proxied(self, v):
        return LazyProxy(lambda: v)


class TestProxyFeatures(unittest.TestCase):
    """Coverage for callback access, caching, forwarding, and wrappers."""

    def test_callback_proxy_get_and_set_callback(self):
        p = CallbackProxy(lambda: 1)
        self.assertEqual(get_callback(p)(), 1)
        self.assertEqual(p.__subject__, 1)
        set_callback(p, lambda: 2)
        self.assertEqual(p.__subject__, 2)
        self.assertEqual(p + 10, 12)

    def test_lazy_proxy_caches_its_callback_result(self):
        calls = []
        def factory():
            calls.append(1)
            return [1, 2, 3]
        p = LazyProxy(factory)
        self.assertEqual(len(p), 3)
        self.assertEqual(len(calls), 1)
        self.assertEqual(p[1], 2)
        self.assertEqual(p.__subject__, [1, 2, 3])
        self.assertEqual(len(calls), 1)

    def test_lazy_proxy_set_subject_replaces_cache(self):
        p = LazyProxy(lambda: [1])
        p.__subject__ = [2, 4]
        self.assertEqual(list(p), [2, 4])

    def test_object_proxy_subject_reassignment(self):
        p = ObjectProxy([1])
        p.__subject__ = [2]
        self.assertEqual(p[0], 2)
        self.assertEqual(len(p), 1)

    def test_attribute_assignment_and_deletion_forward(self):
        class Thing:
            pass
        t = Thing()
        p = ObjectProxy(t)
        p.foo = 5
        self.assertEqual(t.foo, 5)
        self.assertEqual(p.foo, 5)
        del p.foo
        self.assertFalse(hasattr(t, 'foo'))

    def test_item_operations_forward_to_dict(self):
        d = {'a': 1}
        p = ObjectProxy(d)
        p['b'] = 2
        self.assertEqual(d, {'a': 1, 'b': 2})
        self.assertEqual(p['a'], 1)
        del p['a']
        self.assertEqual(d, {'b': 2})
        self.assertIn('b', p)
        self.assertNotIn('z', p)

    def test_callable_proxies_forward_arguments(self):
        def add(a, b):
            return a + b
        p = ObjectProxy(add)
        self.assertEqual(p(1, 2), 3)
        c = CallbackProxy(lambda: add)
        self.assertEqual(c(2, 3), 5)

    def test_object_wrapper_holds_extra_attributes(self):
        class MyList(ObjectWrapper):
            __slots__ = ('extra',)
        w = MyList([])
        w.extra = 42
        self.assertEqual(w.extra, 42)
        w.append(1)
        self.assertEqual(w.__subject__, [1])
        self.assertEqual(list(w), [1])

    def test_callback_wrapper_holds_extra_attributes(self):
        class MyCallback(CallbackWrapper):
            __slots__ = ('tag',)
        w = MyCallback(lambda: [1])
        w.tag = 'x'
        self.assertEqual(w.tag, 'x')
        self.assertEqual(w[0], 1)
        set_callback(w, lambda: [5])
        self.assertEqual(list(w), [5])

    def test_lazy_wrapper_holds_extra_attributes(self):
        class MyLazy(LazyWrapper):
            __slots__ = ('tag',)
        w = MyLazy(lambda: {'k': 9})
        w.tag = 'y'
        self.assertEqual(w.tag, 'y')
        self.assertEqual(w['k'], 9)

    def test_string_proxying(self):
        p = ObjectProxy('hello')
        self.assertEqual(p.upper(), 'HELLO')
        self.assertEqual(len(p), 5)
        self.assertIn('ell', p)
        self.assertEqual('h' + p[1:], 'hello')


def additional_tests():
    return doctest.DocFileSuite(
        'README.md', 'quirky-tests.txt', optionflags=doctest.ELLIPSIS,
    )
