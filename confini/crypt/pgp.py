# standard imports
import logging
import re
import os

# external imports
import gnupg

# local imports
from confini.error import DecryptError


logg = logging.getLogger(__name__)

gpg = gnupg.GPG(
    verbose=False,
    use_agent=True,
        )
gpg.encoding = 'utf-8'



class PGPDecrypter:

    def __init__(self, base_dir='.'):
        self.base_dir = base_dir


    def decrypt(self, k, v, src_dir=None):
        if src_dir == None:
            src_dir = self.base_dir

        if type(v).__name__ != 'str':
            logg.debug('entry {} is not type str'.format(k))
            return (v, False)

        m = re.match(r'^\!gpg\((.*)\)', v)
        if m != None:
            filename = m.group(1)
            if filename[0] != '/':
                filename = os.path.join(src_dir, filename)
            f = open(filename, 'rb')
            logg.debug('decrypting entry {} in file {}'.format(k, f))
            d = gpg.decrypt_file(f)
            if not d.ok:
                raise DecryptError()
            v = str(d)
            f.close()

        return (v, m != None)

    def __str__(self):
        return 'gpg decrypter'
