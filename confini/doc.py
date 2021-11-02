# standard imports
import os
import configparser
import logging

# local imports
from confini.common import to_constant_name

logg = logging.getLogger(__name__)


class ConfigDoc:

    def __init__(self, src):
        fp = os.path.join(src, '.confini')
        logg.debug('attempting doc parser with src {}'.format(fp))

        self.src = fp
        self.docs = {}
        self.docs_flat = {}

        try:
            self.process_as_ini()
        except Exception:
            self.process_as_env()


    def process_as_ini(self):
        p = configparser.ConfigParser()
        p.read_file(self.src)
        return self.process_parser(p)


    def process_as_env(self):
        from confini.env import ConfigEnvParser
        c = ConfigEnvParser()
        p = c.from_file(self.src)
        return self.process_parser(p)


    def process_parser(self, p):
        for ks in p.sections():
            if self.docs.get(ks) == None:
                self.docs[ks] = {}
            for ko in p.options(ks):
                v = p.get(ks, ko)
                self.docs[ks][ko] = v
                c = to_constant_name(ko, ks)
                self.docs_flat[c] = v
                logg.debug('docs {} -> {} = {}'.format(ks, ko, v))


    def get(self, k, o=None):
        if o == None:
            return self.docs_flat[k]
        else:
            return self.docs[k][o]


    @staticmethod
    def from_config(config):
        return ConfigDoc(config.dirs[0])
