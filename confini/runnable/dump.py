# standard imports
import sys
import logging
import argparse
import copy
import os
import stat

# local imports
from confini import Config

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()


argparser = argparse.ArgumentParser()
argparser.add_argument('-z', action='store_true', help='Truncate values in output')
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('--schema-dir', dest='schema_dir', action='append', type=str, help='Configuation directory to merge with schema definitions')
argparser.add_argument('--schema-module', dest='schema_module', action='append', type=str, default=[], help='Module path to merge with schema definitions')
argparser.add_argument('config_dir', nargs='*', type=str, help='Configuation directories to parse')
args = argparser.parse_args()

if args.v:
    logg.setLevel(logging.DEBUG)


def main():
    schema_dirs = []
    for m in args.schema_module:
        md = m.replace('.', '/')
        for i in range(len(sys.path)-1, -1, -1):
            schema_mod_candidate = os.path.join(sys.path[i], md)
            logg.debug('Probing config directory for module {} in {}'.format(m, schema_mod_candidate))
            try:
                s = os.stat(schema_mod_candidate)
                if not stat.S_ISDIR(s.st_mode):
                    continue
                logg.info('Using config directory for module {} in {}'.format(m, schema_mod_candidate))
            except FileNotFoundError:
                continue
            schema_dirs.append(schema_mod_candidate) 

    if args.schema_dir != None:
        schema_dirs += args.schema_dir

    if len(schema_dirs) == 0:
        schema_dirs = None

    c = Config(schema_dirs, override_dirs=args.config_dir)
    c.process()
    for k in c.store.keys():
        v = c.get(k)
        if args.z or v == None:
            v = ''
        print('{}={}'.format(k, v))


if __name__ == "__main__":
    main()
