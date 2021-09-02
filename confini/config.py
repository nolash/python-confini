# standard imports
import logging
import sys
import os
import tempfile
import configparser
import re

# external imports
import gnupg

logg = logging.getLogger('confini')

current_config = None


def set_current(conf, description=''):
    global current_config
    logg.debug('setting current config ({})'.format(description))
    current_config = conf 




class Config:

    parser = configparser.ConfigParser(strict=True)
    default_censor_string = '***'

    def __init__(self, default_dir, env_prefix=None, override_dirs=[]):
        self.__target_tmpdir = None
        if default_dir == None:
            default_dir = override_dirs
        if isinstance(default_dir, list):
            self.collect_from_dirs(default_dir)
        else:
            self.dirs = [default_dir]
        for d in override_dirs:
            if not os.path.isdir(d):
                raise OSError('{} is not a directory'.format(override_dirs))
            self.dirs.append(os.path.realpath(d))
        self.required = {}
        self.censored = {}
        self.store = {}
        self.decrypt = []
        self.env_prefix = None
        self.src_dirs = {}
        if env_prefix != None:
            logg.info('using prefix {} for environment variable override matches'.format(env_prefix))
            self.env_prefix = '{}_'.format(env_prefix)

    def collect_from_dirs(self, dirs):
        self.__target_tmpdir = tempfile.TemporaryDirectory()
        self.dirs = [self.__target_tmpdir.name]
        for i, d in enumerate(dirs):
            for filename_in in os.listdir(d):
                if re.match(r'.+\.ini$', filename_in) == None:
                    continue
                filename_out = '{}_{}'.format(i, filename_in)
                in_filepath = os.path.join(d, filename_in)
                out_filepath = os.path.join(self.dirs[0], filename_out)
                fr = open(in_filepath, 'rb')
                fw = open(out_filepath, 'wb')
                fw.write(fr.read())
                fw.close()
                fr.close()
                logg.debug('base config {} will be processed as {}'.format(in_filepath, out_filepath))
#        return target_dir.name


    def add_decrypt(self, decrypter):
        self.decrypt.append(decrypter)


    def add(self, value, constant_name, exists_ok=False):
        value_stored = self.store.get(constant_name)
        if not self.is_as_none(value_stored):
            if not exists_ok:
                raise AttributeError('config key {} already exists'.format(constant_name))
            else:
                if value_stored != value:
                    logg.debug('updating key {}'.format(constant_name))
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


    def _sections_override(self, dct, dct_description):
        for s in self.parser.sections():
            for k in self.parser[s]:
                cn = Config.to_constant_name(k, s)
                self.override(cn, self.parser[s][k], dct, dct_description)


    def dict_override(self, dct, dct_description):
        for k in dct.keys():
            try:
                self.override(k, self.store[k], dct, dct_description)
            except KeyError:
                logg.warning('override key {} have no match in config store'.format(k))


    def override(self, cn, v, dct, dct_description):
        cn_env = cn
        if self.env_prefix != None:
            cn_env = self.env_prefix + cn
        val = dct.get(cn_env)
        if val == None or val == '':
            val = self.store.get(cn, v)
        else:
            logg.info('{} {} overrides {}'.format(dct_description, cn_env, cn))
        self.add(val, cn, exists_ok=True)


    def set_dir(self, k, d):
        logg.debug('set dir {} for key {}'.format(d, k))
        self.src_dirs[k] = d


    def process(self, set_as_current=False):
        """Concatenates all .ini files in the config directory attribute and parses them to memory
        """
        tmp_dir = tempfile.mkdtemp()
        logg.debug('using tmp processing dir {}'.format(tmp_dir))
        for i, d in enumerate(self.dirs):
            d = os.path.realpath(d)
            if i == 0:
                d_label = 'default'
            else:
                d_label = 'override #' + str(i)
            tmp_out_dir = os.path.join(tmp_dir, str(i))
            os.makedirs(tmp_out_dir)
            logg.debug('processing dir {} ({})'.format(d, d_label))
            tmp_out = open(os.path.join(tmp_out_dir, 'config.ini'), 'ab')
            for filename in os.listdir(d):
                if re.match(r'.+\.ini$', filename) == None:
                    logg.debug('skipping file {}/{}'.format(d, filename))
                    continue
                logg.info('reading file {}/{}'.format(d, filename))
                f = open(os.path.join(d, filename), 'rb')
                while 1:
                    data = f.read()
                    if not data:
                        break
                    tmp_out.write(data)
                f.close()
            tmp_out.close()
        d = os.listdir(tmp_dir)
        d.sort()
        c = 0

        # TODO: this will fail of sections/options are repeated. should first use individual parser instances to flatten to single file (perhaps in collect_from_dirs already)
        for i, tmp_config_dir in enumerate(d):
            tmp_config_dir = os.path.join(tmp_dir, tmp_config_dir)
            for tmp_file in os.listdir(os.path.join(tmp_config_dir)):
                tmp_config_file_path = os.path.join(tmp_config_dir, tmp_file)
                if c == 0:
                    logg.debug('apply default parser for config directory {}'.format(self.dirs[i]))
                    self.parser.read(tmp_config_file_path)
                    for s in self.parser.sections():
                        for so in self.parser.options(s):
                            k = self.to_constant_name(so, s)
                            v = self.parser.get(s, so)
                            logg.debug('default config set {}'.format(k))
                            self.add(v, k, exists_ok=True)
                            self.set_dir(k, self.dirs[i])
                else:
                    logg.debug('apply override parser for config directory {}'.format(self.dirs[i]))
                    local_parser = configparser.ConfigParser(strict=True)
                    local_parser.read(tmp_config_file_path)
                    for s in local_parser.sections():
                        for so in local_parser.options(s):
                            k = self.to_constant_name(so, s)
                            if not self.have(k):
                                raise KeyError('config overrides in {} defines key {} not present in default config {}'.format(self.dirs[i], k, self.dirs[0]))
                            v = local_parser.get(s, so)
                            logg.debug('checking {} {} {}'.format(k, s, so))
                            if not self.is_as_none(v):
                                logg.debug('multi config file overrides {}'.format(k))
                                self.add(v, k, exists_ok=True)
                                self.set_dir(k, self.dirs[i])
            c += 1
        self._sections_override(os.environ, 'environment variable')
        if set_as_current:
            set_current(self, description=self.dir)


    def _decrypt(self, k, v, src_dir):
        if len(self.decrypt) == 0:
            return v
        for decrypter in self.decrypt:
            logg.debug('applying decrypt with {}'.format(str(decrypter)))
            (v, r) = decrypter.decrypt(k, v, src_dir)
            if r:
                return v
        return v


    def get(self, k, default=None):
        v = self.store[k]
        if v == None:
            if default != None:
                logg.debug('returning default value for empty value {}'.format(k))
            return default
        if self.is_as_none(v): 
            if default != None:
                logg.debug('returning default value for empty string value {}'.format(k))
                return default
            else:
                return None

        return self._decrypt(k, v, self.src_dirs.get(k))


    def have(self, k):
        try:
            v = self.store[k]
            return True
        except KeyError:
            return False


    def all(self):
        return list(self.store.keys())


    def true(self, k):
        v = self.store.get(k)
        if type(v).__name__ == 'bool':
            logg.debug('entry {} is already bool'.format(k))
            return v
        d = self._decrypt(k, v, self.src_dirs.get(k))
        if d.lower() not in ['true', 'false', '0', '1', 'on', 'off']:
            raise ValueError('{} not a boolean value'.format(k))
        return d.lower() in ['true', '1', 'on']


    def apply_censor(self, k):
        try:
            _ = self.censored[k]
            return self.default_censor_string
        except KeyError:
            return self.store[k]


    def __str__(self):
        ls = []
        for k in self.store.keys():
            v = self.apply_censor(k)
            ls.append('{}={}'.format(k, v))

        return '\n'.join(ls)


    def __repr__(self):
        return "<Config '{}'>".format(self.dir)


    @classmethod
    def is_as_none(cls, v):
        if isinstance(v, str) and v == '':
            return True
        if v == None:
            return True


def config_from_environment():
    config_dir = config_dir_from_environment()
    c = Config(config_dir)
    c.process()
    return c


def config_dir_from_environment():
    return os.environ.get('CONFINI_DIR')
