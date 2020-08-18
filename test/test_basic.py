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


    def test_require(self):
        inidir = os.path.join(self.wd, 'files')
        c = Config(inidir)
        c.require('BERT', 'XYZZY')
        self.assertTrue(c.validate())
        c.require('ERNIE', 'XYZZY')
        self.assertFalse(c.validate())
        logg.debug(c)

if __name__ == '__main__':
    unittest.main()
