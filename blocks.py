import json
import sys

if sys.version_info >= (3, 0):
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

class Blocks:

    def __init__(self):
        self.version = None
        self.block_hash = None

    def load_info(self, block_number):
        raise NotImplementError

    def read_url(self, url):
        try:
            return urlopen(url).read().decode('utf-8')
        except:
            print('Error trying to read: ' + url +\
                    ' / Try to open in a browser to see what the error is.')
            sys.exit(0)

class Block_Toshi(Blocks):

    def __init__(self):
        TOSHI_API = 'https://bitcoin.toshi.io/api'
        self.url = TOSHI_API + "/v0/blocks/{}"

    def load_info(self, block_number):
        json_block = json.loads(self.read_url(self.url.format(str(block_number))))
        self.version = json_block['version']
        self.block_hash = json_block['hash']

