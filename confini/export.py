# import 
import sys
import configparser
import os
import stat
import enum
import io
import logging

logg = logging.getLogger(__name__)


class ConfigExporterTarget(enum.Enum):
    HANDLE = 1
    FILE = 2
    DIR = 3


class ConfigExporter:

    def __init__(self, config, target=None, split=False, doc=False):
        self.config = config
        self.sections = {}
        self.target_split = split
        self.target_typ = ConfigExporterTarget.HANDLE
        self.target = None
        self.make_doc = doc
        self.doc = None
        if isinstance(target, io.IOBase):
            self.target = target
        else:
            st = os.stat(target)
            if stat.S_ISDIR(st.st_mode):
                self.target_typ = ConfigExporterTarget.DIR
                self.target = os.path.realpath(target)
            else:
                self.target_typ = ConfigExporterTarget.FILE
                d = os.getcwd()
                self.target = os.path.join(d, target)

        if self.make_doc:
            from confini.doc import ConfigDoc
            self.doc = ConfigDoc.from_config(config)


    def scan(self):
        for k in self.config.all():
            (s, v) = k.split('_', maxsplit=1)
            s = s.lower()
            v = v.lower()
            if self.sections.get(s) == None:
                self.sections[s] = {}
            self.sections[s][v] = self.config.get(k)


    def export_section(self, ks, w):
        w.write("[" + ks + "]\n")
        for ko in self.sections[ks].keys():
            if self.make_doc:
                try:
                    v = self.doc.get(ks, ko)
                    w.write("# " + v + "\n")
                except KeyError:
                    logg.warning('doc missing for section {} option {}'.format(ks, ko))
                    pass
            w.write(ko + " = " + self.sections[ks][ko] + "\n")
        w.write("\n")


    def export(self):
        self.scan()

        w = None
        if self.target_typ == ConfigExporterTarget.HANDLE:
            w = self.target

        for k in self.sections:
            if w != None:
                self.export_section(k, w)
                continue

            if self.target_typ == ConfigExporterTarget.FILE:
                w = open(self.target, 'a')
            elif self.target_typ == ConfigExporterTarget.DIR:
                if self.target_split:
                    fn = k + '.ini'
                else:
                    fn = 'config.ini'
                fp = os.path.join(self.target, fn)
                w = open(fp, 'a')

            self.export_section(k, w)

            w.close()
            w = None
