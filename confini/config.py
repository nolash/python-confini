#!/usr/bin/python

import logging
import sys
import os
import tempfile
import configparser
import re
import gnupg

logg = logging.getLogger()

current_config = None

gpg = gnupg.GPG(
    verbose=False,
    use_agent=True,
        )
gpg.encoding = 'utf-8'


def set_current(conf, description=''):
    global current_config
    logg.debug('setting current config ({})'.format(description))
    current_config = conf 


class Config:

    parser = configparser.ConfigParser(strict=True)

    def __init__(self, config_dir, decrypt=True):
        if not os.path.isdir(config_dir):
            raise OSError('{} is not a directory'.format(config_dir))
        self.dir = os.path.realpath(config_dir)
        self.required = {}
        self.censored = {}
        self.store = {}
        self.decrypt = decrypt


    def add(self, value, constant_name):
        self.store[constant_name] = value


    def censor(self, identifier, section=None):
        constant_name = ''
        if section != None:
            constant_name = Config.to_constant_name(identifier, section)
        else:
            constant_name = identifier
        self.censored[constant_name] = True


    def require(self, directive, section):
        if self.required.get(section) == None:
            self.required[section] = []
        self.required[section].append(directive)


    def validate(self):
        for k in self.required.keys():
            for v in self.required[k]:
                try:
                    _ = self.parser[k][v]
                except:
                    return False
        return True


    @staticmethod
    def to_constant_name(directive, section):
        return '{}_{}'.format(section.upper(), directive.upper())


    def _process_env(self):
        for s in self.parser.sections():
            for k in self.parser[s]:
                cn = Config.to_constant_name(k, s)
                self.add(os.environ.get(cn, self.parser[s][k]), cn)


    def process(self, set_as_current=False):
        """Concatenates all .ini files in the config directory attribute and parses them to memory
        """
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmpname = tmp.name
        for filename in os.listdir(self.dir):
            if re.match(r'.+\.ini$', filename) == None:
                logg.debug('skipping file {}'.format(filename))
                continue
            logg.info('reading file {}'.format(filename))
            f = open(os.path.join(self.dir, filename), 'rb')
            while 1:
                data = f.read()
                if not data:
                    break
                tmp.write(data)
            f.close()
        tmp.close()
        self.parser.read(tmpname)
        os.unlink(tmpname)
        self._process_env()
        if set_as_current:
            set_current(self, description=self.dir)



    def _decrypt(self, k, v):
        if self.decrypt:
            m = re.match(r'^\!gpg\((.*)\)', v)
            if m != None:
                filename = m.group(1)
                if filename[0] != '/':
                    filename = os.path.join(self.dir, filename)
                f = open(filename, 'rb')
                logg.debug('decrypting entry {} in file {}'.format(k, f))
                v = gpg.decrypt_file(f)
                f.close()
        return v


    def get(self, k):
        v = self.store.get(k)
        return self._decrypt(k, v)


    def __str__(self):
        ls = []
        for k in self.store.keys():
            v = ''
            try:
                _ = self.censored[k]
                v = '***'
            except:
                v = self.store[k]

            ls.append('{} = {}'.format(k, v))

        return '\n'.join(ls)


    def __repr__(self):
        return "<Config '{}'>".format(self.dir)



def config_from_environment():
    config_dir = config_dir_from_environment()
    c = Config(config_dir)
    c.process()
    return c


def config_dir_from_environment():
    return os.environ.get('CIC_CONFIG_DIR')


