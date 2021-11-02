#!/usr/bin/python

import os
import unittest
import logging

from confini import Config

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class TestBasic(unittest.TestCase):

    wd = os.path.dirname(__file__)

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_parse_two(self):
        inidir_one = os.path.join(self.wd, 'files', 'multi', 'one')
        inidir_two = os.path.join(self.wd, 'files', 'multi', 'two')
        c = Config(inidir_one, override_dirs=[inidir_two])
        c.process()
        r = c.get('FOO_BAR')
        self.assertEqual(r, 'plugh')
        r = c.get('FOO_BAZ')
        self.assertEqual(r, '42')
        r = c.get('FOO_BAH')
        self.assertEqual(r, None)
        r = c.get('BAR_ONE')
        self.assertEqual(r, 'three')


    def test_parse_two_schema_error(self):
        inidir_one = os.path.join(self.wd, 'files', 'multi', 'one')
        inidir_two = os.path.join(self.wd, 'files', 'multi', 'three')
        c = Config(inidir_one, override_dirs=[inidir_two])
        with self.assertRaises(KeyError):
            c.process()
        
        

if __name__ == '__main__':
    unittest.main()
