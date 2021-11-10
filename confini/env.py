# standard imports
import configparser
import io
import logging
import sys

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
            try:
                (ks, ko) = k.split('_', maxsplit=1)
            except ValueError:
                ks = k
                ko = '_'
            ks = ks.lower()
            ko = ko.lower()
            v = v.rstrip()
            if not self.parser.has_section(ks):
                self.parser.add_section(ks)
            self.parser.set(ks, ko, v)
        return self.parser


def export_env(config, prefix=None, empty_all=False, skip_empty=False, doc=False, w=sys.stdout):
    for k in config.all():
        if k[0] == '_':
            continue
        v = config.get(k)
        if empty_all or v == None:
            v = ''
        if v == '' and skip_empty:
            logg.debug('skipping empty directive {}'.format(k))
            continue
        if doc:
            try:
                doc_s = config.doc.get(k)
                w.write('# ' + doc_s + "\n")
            except KeyError:
                pass
        if prefix != None:
            w.write(prefix + ' ')
        w.write('{}={}\n'.format(k, v))
