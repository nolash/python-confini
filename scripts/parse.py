import sys
import logging

from confini import Config

#logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write('usage: config.py <config_dir>')
        sys.exit(1)
    c = Config(sys.argv[1])
    c.process()
    for k in c.store.keys():
        print('{}: {}'.format(k, c.get(k)))
