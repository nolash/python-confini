import sys

from confini import Config

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write('usage: config.py <config_dir>')
        sys.exit(1)
    c = Config(sys.argv[1])
    c.process()
    print(c)
