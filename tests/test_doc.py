# standard imports
import unittest
import os
import logging

# local imports
from confini import Config
from confini.doc import ConfigDoc

logging.basicConfig(level=logging.DEBUG)


class TestDoc(unittest.TestCase):

    wd = os.path.dirname(__file__)

    def test_from_config(self):
        inidir = os.path.join(self.wd, 'files/doc/ok')
        c = Config(inidir)
        c.process()

        doc = ConfigDoc.from_config(c)
        self.assertEqual(doc.get('FOO_BAR'), 'foo of bar')
        self.assertEqual(doc.get('BAR_XYZZY'), 'bar of xyzzy')


if __name__ == '__main__':
    unittest.main()
