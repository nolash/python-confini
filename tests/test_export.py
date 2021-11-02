# standard imports
import os
import io
import unittest
import logging
import configparser
import tempfile
import re

# local imports
from confini import Config
from confini.export import ConfigExporter
from confini.doc import ConfigDoc

logging.basicConfig(level=logging.DEBUG)

logg = logging.getLogger()


class TestExport(unittest.TestCase):

    wd = os.path.dirname(__file__)


    def setUp(self):
        self.inidir = os.path.join(self.wd, 'files')
        c = Config(self.inidir)
        c.process()
        self.config = c


    def test_handle(self):
        w = io.StringIO()
        e = ConfigExporter(self.config, target=w)
        e.export()

        w.seek(0)
        a = configparser.ConfigParser()
        a.read_string(w.read())

        b = configparser.ConfigParser()
        b.read(os.path.join(self.inidir, 'foo.ini'))
        b.read(os.path.join(self.inidir, 'bar.ini'))

        for s in b.sections():
            for o in b.options(s):
                self.assertEqual(b.get(s, o), a.get(s.lower(), o.lower()))


    def test_file(self):
        (fd, fn) = tempfile.mkstemp()
        e = ConfigExporter(self.config, target=fn)
        e.export()

        w = os.fdopen(fd)
        a = configparser.ConfigParser()
        a.read_string(w.read())

        b = configparser.ConfigParser()
        b.read(os.path.join(self.inidir, 'foo.ini'))
        b.read(os.path.join(self.inidir, 'bar.ini'))

        for s in b.sections():
            for o in b.options(s):
                self.assertEqual(b.get(s, o), a.get(s.lower(), o.lower()))


    def test_dir_file(self):
        d = tempfile.mkdtemp()
        e = ConfigExporter(self.config, target=d)
        e.export()

        a = configparser.ConfigParser()
        a.read(os.path.join(d, 'config.ini'))

        b = configparser.ConfigParser()
        b.read(os.path.join(self.inidir, 'foo.ini'))
        b.read(os.path.join(self.inidir, 'bar.ini'))

        for s in b.sections():
            for o in b.options(s):
                self.assertEqual(b.get(s, o), a.get(s.lower(), o.lower()))


    def test_dir_split(self):
        d = tempfile.mkdtemp()
        e = ConfigExporter(self.config, target=d, split=True)
        e.export()

        a = configparser.ConfigParser()
        a.read(os.path.join(d, 'foo.ini'))
        a.read(os.path.join(d, 'bar.ini'))
        a.read(os.path.join(d, 'xyzzy.ini'))

        b = configparser.ConfigParser()
        b.read(os.path.join(self.inidir, 'foo.ini'))
        b.read(os.path.join(self.inidir, 'bar.ini'))

        for s in b.sections():
            for o in b.options(s):
                self.assertEqual(b.get(s, o), a.get(s.lower(), o.lower()))



    def test_doc(self):
        w = io.StringIO()
        e = ConfigExporter(self.config, target=w, doc=True)
        e.export()
    
        w.seek(0)
        s = w.read()

        print(s)
        re_c = re.compile('^# ', re.MULTILINE)
        m = re_c.finditer(s)
        next(m)
        next(m)
        next(m)
        with self.assertRaises(StopIteration):
            next(m)

        re_c = re.compile('^# .*foo$', re.MULTILINE)
        m = re_c.finditer(s)
        next(m)
        next(m)
        with self.assertRaises(StopIteration):
            next(m)

        a = configparser.ConfigParser()
        a.read_string(s)

        b = configparser.ConfigParser()
        b.read(os.path.join(self.inidir, 'foo.ini'))
        b.read(os.path.join(self.inidir, 'bar.ini'))

        for s in b.sections():
            for o in b.options(s):
                self.assertEqual(b.get(s, o), a.get(s.lower(), o.lower()))


if __name__ == '__main__':
    unittest.main()
