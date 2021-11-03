# standard imports
import os
import configparser
import logging

# local imports
from confini.common import to_constant_name

logg = logging.getLogger(__name__)


class ConfigDoc:

    def __init__(self, src=None):
        fp = None
        if src != None:
            fp = os.path.join(src, '.confini')
            logg.debug('attempting doc parser with src {}'.format(fp))

        self.src = fp
        self.docs = {}
        self.docs_flat = {}

        if self.src != None:
            self.process(self.src)
           

    def process(self, src):
        try:
            self.process_as_ini(src)
        except Exception:
            self.process_as_env(src)


    def process_as_ini(self, src):
        p = configparser.ConfigParser()
        p.read_file(src)
        return self.process_parser(p)


    def process_as_env(self, src):
        from confini.env import ConfigEnvParser
        c = ConfigEnvParser()
        p = c.from_file(src)
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

    
    def all(self):
        return list(self.docs_flat.keys())


    @staticmethod
    def from_config(config):
        if config.doc != None:
            return config.doc
        return ConfigDoc(config.dirs[0])
