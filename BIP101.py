"""
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# IMPORTS

import sys
if sys.version_info >= (3, 0):
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

import json
import sqlite3
import argparse


#
# CONSTANTS
#
BLOCK_API = 'https://blockexplorer.com/api'
BLOCK_INDEX_URL = BLOCK_API + '/block-index/'
BLOCK_URL = BLOCK_API + '/block/'
GETBLOCKCOUNT_URL = 'https://blockchain.info/q/getblockcount'
DB_BLOCKCHAIN = 'local_blockchain.db'
PREVIOUS_BLOCKS = 1000

BICOIN_CORE = '3'
BITCOIN_XT = '536870919'

VERSION_BLOCK = {
    BICOIN_CORE: "Bitcoin Core",
    BITCOIN_XT: 'Bitcoin XT'
}

__version__ = '0.3'

parser = argparse.ArgumentParser(description="List blocks version.")

parser.add_argument('--list-BIP101', action='store_true', help='List all the BIP101 blocks and their hashes')
parser.add_argument('--version', '-v', action='store_true', help='Show version')
args = parser.parse_args()

if args.version:
    print('Version ' + __version__)
    exit(0)


conn = sqlite3.connect(DB_BLOCKCHAIN)

c = conn.cursor()

def create_table():
    blockchain_table = c.execute("select name from sqlite_master where type = 'table' and name = 'blockchain'")

    if len(blockchain_table.fetchall()) == 0:
        c.execute("create table blockchain (block int, version int, hash text)")

def get_highest_block():
    highest_block = read_url(GETBLOCKCOUNT_URL)

    return int(highest_block)

def get_latest_block():
    block = get_highest_block() - PREVIOUS_BLOCKS

    return block

def get_latest_fetched_block():
    sql = c.execute('select block from blockchain order by block desc limit 1')
    return sql.fetchone()[0] + 1

def set_block():
    if len(c.execute("select * from blockchain").fetchall()) == 0:
        block = get_latest_block()
    else:
        block = get_latest_fetched_block()

        return block

def read_url(url):
    try:
        return urlopen(url).read().decode('utf-8')
    except:
        print('Error trying to read: ' + url)
        sys.exit(0)

def insert_blocks(block):
    for i in range(block, get_highest_block()):
        block_hash = json.loads(read_url(BLOCK_INDEX_URL + str(i)))

        block_info = json.loads(read_url(BLOCK_URL + block_hash['blockHash']))

        insert_sql = "INSERT INTO blockchain (block, version, hash) values "
        insert_sql += " (" + str(i) + ", "
        insert_sql += str(block_info['version']) + ", "
        insert_sql += "'" + block_hash['blockHash'] + "'"
        insert_sql += ")"

        c.execute(insert_sql)
        print('Inserted block: ' + str(i))

    conn.commit()

def show_block_summary():
    result = c.execute("select version, count(version) as ver from (select * from blockchain order by block desc limit 1000) group by version")

    print("\nLatest: " + str(PREVIOUS_BLOCKS)+ " blocks\n")
    for i in result:
        if str(i[0]) in VERSION_BLOCK.keys():
            print(str(i[1]) + " mined with " + VERSION_BLOCK[str(i[0])])
        else:
            print(str(i[1]) + " mined with unknown version")


    print("\n")

def show_BIP101_blocks():
    result = c.execute('select hash from blockchain where version = ' + BITCOIN_XT)

    print('Hashes of the BIP101 blocks: ')

    for i in result:
        print(str(i[0]))

create_table()
get_latest_block()
get_latest_fetched_block()
insert_blocks(set_block())

if args.list_BIP101:
    show_BIP101_blocks()
else:
    show_block_summary()

conn.close()

