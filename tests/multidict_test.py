# -*- coding: utf-8 -*-

import unittest
from aiorest import multidict

class BaseDictTestsMixin:
    def setUp(self):
        self._list = [('a', '\xe9'), ('a', 'e'), ('a', 'f'), ('b', '1')]
        self.data = multidict.MultiDict(self._list)
        self.d = self._get_instance()

    def _get_instance(self, **kwargs):
        if kwargs:
            data = multidict.MultiDict(kwargs)
        else:
            data = self.data.copy()
        return self.klass(data)

    def test_len(self):
        self.assertEqual(len(self.d), 4)

    def test_getone(self):
        self.assertEqual(self.d.getone('b'),  '1')

    def test_getone_missing(self):
        self.assertRaises(KeyError, self.d.getone, 'z')

    def test_getone_multiple_raises(self):
        self.assertRaises(KeyError, self.d.getone, 'a')

    def test_getall(self):
        self.assertEqual(list(self.d.getall('b')), ['1'])

    def test_dict_of_lists(self):
        self.assertEqual(
            self.d.dict_of_lists(),
            {'a': ['\xe9', 'e', 'f'], 'b': ['1']})

    def test_dict_api(self):
        self.assertTrue('a' in self.d.mixed())
        self.assertTrue('a' in self.d.keys())
        self.assertTrue('a' in self.d.iterkeys())
        self.assertTrue(('b', '1') in self.d.items())
        self.assertTrue(('b', '1') in self.d.iteritems())
        self.assertTrue('1' in self.d.values())
        self.assertTrue('1' in self.d.itervalues())
        self.assertEqual(len(self.d), 4)

    def test_set_del_item(self):
        d = self._get_instance()
        self.assertTrue('a' in d)
        del d['a']
        self.assertTrue(not 'a' in d)

    def test_pop(self):
        d = self._get_instance()
        d['a'] = '1'
        self.assertEqual(d.pop('a'), '1')
        self.assertEqual(d.pop('x', '1'), '1')

    def test_pop_wrong_args(self):
        d = self._get_instance()
        self.assertRaises(TypeError, d.pop, 'a', '1', '1')

    def test_pop_missing(self):
        d = self._get_instance()
        self.assertRaises(KeyError, d.pop, 'z')

    def test_popitem(self):
        d = self._get_instance()
        self.assertEqual(d.popitem(), ('b', '1'))

    def test_update(self):
        d = self._get_instance()
        d.update(e='1')
        self.assertTrue('e' in d)
        d.update(dict(x='1'))
        self.assertTrue('x' in d)
        d.update([('y', '1')])
        self.assertTrue('y' in d)

    def test_setdefault(self):
        d = self._get_instance()
        d.setdefault('a', '1')
        self.assertNotEqual(d['a'], '1')
        d.setdefault('e', '1')
        self.assertTrue('e' in d)

    def test_add(self):
        d = multidict.MultiDict({'a': '1'})
        d.add('a', '2')
        self.assertEqual(list(d.getall('a')), ['1', '2'])
        d = self._get_instance()
        d.add('b', '3')
        self.assertEqual(list(d.getall('b')), ['1', '3'])

    def test_copy(self):
        assert self.d.copy() is not self.d
        if hasattr(self.d, 'multi'):
            self.assertFalse(self.d.copy().multi is self.d.multi)
            self.assertFalse(self.d.copy() is self.d.multi)

    def test_clear(self):
        d = self._get_instance()
        d.clear()
        self.assertEqual(len(d), 0)

    def test_nonzero(self):
        d = self._get_instance()
        self.assertTrue(d)
        d.clear()
        self.assertFalse(d)

    def test_repr(self):
        self.assertTrue(repr(self._get_instance()))

    def test_too_many_args(self):
        from webob.multidict import MultiDict
        self.assertRaises(TypeError, MultiDict, '1', 2)

    def test_no_args(self):
        from webob.multidict import MultiDict
        md = MultiDict()
        self.assertEqual(md._items, [])

    def test_kwargs(self):
        from webob.multidict import MultiDict
        md = MultiDict(kw1='val1')
        self.assertEqual(md._items, [('kw1','val1')])

    def test_view_list_not_list(self):
        from webob.multidict import MultiDict
        d = MultiDict()
        self.assertRaises(TypeError, d.view_list, 42)

    def test_view_list(self):
        from webob.multidict import MultiDict
        d = MultiDict()
        self.assertEqual(d.view_list([1,2])._items, [1,2])

    def test_from_fieldstorage_with_filename(self):
        from webob.multidict import MultiDict
        d = MultiDict()
        fs = DummyFieldStorage('a', '1', 'file')
        self.assertEqual(d.from_fieldstorage(fs), MultiDict({'a':fs.list[0]}))

    def test_from_fieldstorage_without_filename(self):
        from webob.multidict import MultiDict
        d = MultiDict()
        fs = DummyFieldStorage('a', '1')
        self.assertEqual(d.from_fieldstorage(fs), MultiDict({'a':'1'}))

    def xtest_from_fieldstorage_with_charset(self):
        from cgi import FieldStorage
        from webob.request import BaseRequest
        from webob.multidict import MultiDict
        multipart_type = 'multipart/form-data; boundary=foobar'
        from io import BytesIO
        body = (
            b'--foobar\r\n'
            b'Content-Disposition: form-data; name="title"\r\n'
            b'Content-type: text/plain; charset="ISO-2022-JP"\r\n'
            b'\r\n'
            b'\x1b$B$3$s$K$A$O\x1b(B'
            b'\r\n'
            b'--foobar--')
        multipart_body = BytesIO(body)
        environ = BaseRequest.blank('/').environ
        environ.update(CONTENT_TYPE=multipart_type)
        environ.update(REQUEST_METHOD='POST')
        environ.update(CONTENT_LENGTH=len(body))
        fs = FieldStorage(multipart_body, environ=environ)
        vars = MultiDict.from_fieldstorage(fs)
        self.assertEqual(vars['title'].encode('utf8'),
                         ('ã“ã‚“ã«ã¡ã¯').encode('utf8'))

    def xtest_from_fieldstorage_with_base64_encoding(self):
        from cgi import FieldStorage
        from webob.request import BaseRequest
        from webob.multidict import MultiDict
        multipart_type = 'multipart/form-data; boundary=foobar'
        from io import BytesIO
        body = (
            b'--foobar\r\n'
            b'Content-Disposition: form-data; name="title"\r\n'
            b'Content-type: text/plain; charset="ISO-2022-JP"\r\n'
            b'Content-Transfer-Encoding: base64\r\n'
            b'\r\n'
            b'GyRCJDMkcyRLJEEkTxsoQg=='
            b'\r\n'
            b'--foobar--')
        multipart_body = BytesIO(body)
        environ = BaseRequest.blank('/').environ
        environ.update(CONTENT_TYPE=multipart_type)
        environ.update(REQUEST_METHOD='POST')
        environ.update(CONTENT_LENGTH=len(body))
        fs = FieldStorage(multipart_body, environ=environ)
        vars = MultiDict.from_fieldstorage(fs)
        self.assertEqual(vars['title'].encode('utf8'),
                         text_('ã“ã‚“ã«ã¡ã¯', 'utf8').encode('utf8'))

    def xtest_from_fieldstorage_with_quoted_printable_encoding(self):
        from cgi import FieldStorage
        from webob.request import BaseRequest
        from webob.multidict import MultiDict
        multipart_type = 'multipart/form-data; boundary=foobar'
        from io import BytesIO
        body = (
            b'--foobar\r\n'
            b'Content-Disposition: form-data; name="title"\r\n'
            b'Content-type: text/plain; charset="ISO-2022-JP"\r\n'
            b'Content-Transfer-Encoding: quoted-printable\r\n'
            b'\r\n'
            b'=1B$B$3$s$K$A$O=1B(B'
            b'\r\n'
            b'--foobar--')
        multipart_body = BytesIO(body)
        environ = BaseRequest.blank('/').environ
        environ.update(CONTENT_TYPE=multipart_type)
        environ.update(REQUEST_METHOD='POST')
        environ.update(CONTENT_LENGTH=len(body))
        fs = FieldStorage(multipart_body, environ=environ)
        vars = MultiDict.from_fieldstorage(fs)
        self.assertEqual(vars['title'].encode('utf8'),
                         text_('ã“ã‚“ã«ã¡ã¯', 'utf8').encode('utf8'))


class MultiDictTests(BaseDictTestsMixin, unittest.TestCase):
    klass = multidict.MultiDict

    def test_update_behavior_warning(self):
        import warnings
        class Foo(dict):
            def __len__(self):
                return 0
        foo = Foo()
        foo['a'] = 1
        d = self._get_instance()
        with warnings.catch_warnings(record=True) as w:
            d.update(foo)
        self.assertEqual(len(w), 1)

    def test_repr_with_password(self):
        d = self._get_instance(password='pwd')
        self.assertEqual(repr(d), "MultiDict([('password', '******')])")



class DummyField:
    def __init__(self, name, value, filename=None):
        self.name = name
        self.value = value
        self.filename = filename
        self.type_options = {}
        self.headers = {}

class DummyFieldStorage:
    def __init__(self, name, value, filename=None):
        self.list = [DummyField(name, value, filename)]
