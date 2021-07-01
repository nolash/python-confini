# standard imports
import os
import unittest
import logging

# local imports
from confini import Config

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


 
class TestCensor(unittest.TestCase):

    wd = os.path.dirname(__file__)

    def test_censor(self):
        inidir = os.path.join(self.wd, 'files/translate')
        c = Config(inidir)
        c.process()
        c.censor('foo', 'bar')
        v = c.apply_censor('BAR_FOO')

        for k in c.all():
            try:
                assert v == Config.default_censor_string
            except AssertionError:
                self.assertNotEqual('BAR_FOO', k)
            

if __name__ == '__main__':
    unittest.main()
