#!/usr/bin/python

import os
import unittest
import logging

from confini import Config

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()

class TestBasic(unittest.TestCase):

    wd = os.path.dirname(__file__)

    def test_parse_default(self):
        inidir = os.path.join(self.wd, 'files/default')
        c = Config(inidir)
        c.process()
        r = c.get('FOO_BAR', 'plugh')
        self.assertEqual(r, 'xyzzy')
        r = c.get('FOO_BAZ', 'plugh')
        self.assertEqual(r, 'plugh')
        r = c.get('FOO_BAZ')
        self.assertEqual(r, None)
        with self.assertRaises(KeyError):
            r = c.get('FOO_BAZBAZ')


    def test_parse_two(self):
        inidir = os.path.join(self.wd, 'files/default')
        c = Config(inidir, override_dirs=[inidir])
        c.process()
        r = c.get('FOO_BAR', 'plugh')
        self.assertEqual(r, 'xyzzy')
        r = c.get('FOO_BAZ', 'plugh')
        self.assertEqual(r, 'plugh')
        r = c.get('FOO_BAZ')
        self.assertEqual(r, None)
        with self.assertRaises(KeyError):
            r = c.get('FOO_BAZBAZ')


    def test_overwrite_guard(self):
        inidir = os.path.join(self.wd, 'files/default')
        c = Config(inidir)
        c.process()
        with self.assertRaises(AttributeError):
            c.add('xxx', 'FOO_BAR')
        c.add('xxx', 'FOO_BAR', exists_ok=True)
        r = c.get('FOO_BAR')
        self.assertEqual(r, 'xxx')


    def test_parse_two_files(self):
        inidir = os.path.join(self.wd, 'files')
        c = Config(inidir)
        c.process()
        c.require('BERT', 'XYZZY')
        expect = {
            'FOO_BAR': '42',
            'FOO_BAZ': '029a',
            'BAR_FOO': 'oof',
            'XYZZY_BERT': 'ernie',
                }
        self.assertDictEqual(expect, c.store)


    def test_remove_require(self):
        inidir = os.path.join(self.wd, 'files')
        c = Config(inidir)
        c.process()
        c.require('BERT', 'XYZZY')
        self.assertTrue(c.validate())
        c.require('ERNIE', 'XYZZY')
        self.assertFalse(c.validate())
        logg.debug(c)


    def test_remove_strict(self):
        inidir = os.path.join(self.wd, 'files/default')
        c = Config(inidir)
        c.process()
        c.remove('FOO_BAR')
        with self.assertRaises(KeyError):
            c.get('FOO_BAR')


    def test_remove_wild(self):
        inidir = os.path.join(self.wd, 'files/remove')
        c = Config(inidir)
        c.process()
        c.remove('FOO', strict=False)
        self.assertEqual(len(c.all()), 0)

        c = Config(inidir)
        c.process()
        c.remove('FOO_BA', strict=False)
        c.get('FOO_XYZZY') 
        self.assertEqual(len(c.all()), 1)


    def test_all(self):
        inidir = os.path.join(self.wd, 'files')
        c = Config(inidir)
        a = c.all()
        self.assertEqual(a, list(c.store.keys()))


if __name__ == '__main__':
    unittest.main()
