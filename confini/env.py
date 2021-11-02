# standard imports
import configparser
import io
import logging

logg = logging.getLogger(__name__)


class ConfigEnvParser:
    
    def __init__(self):
        self.parser = configparser.ConfigParser()


    def from_file(self, fp):
        f = open(fp, 'r')
        r = self.from_handle(f)
        f.close()
        return r


    def from_string(self, s):
        fh = io.StringIO(s)
        return self.from_handle(fh)


    def from_handle(self, fh):
        while True:
            l = fh.readline()
            if len(l) == 0:
                break
            (k, v) = l.split('=')
            (ks, ko) = k.split('_', maxsplit=1)
            ks = ks.lower()
            ko = ko.lower()
            v = v.rstrip()
            if not self.parser.has_section(ks):
                self.parser.add_section(ks)
            self.parser.set(ks, ko, v)
        return self.parser
