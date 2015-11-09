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

__version__ = '0.7'


TOSHI_API = 'https://bitcoin.toshi.io/api'
BLOCK_INDEX_URL = TOSHI_API + "/v0/blocks/{}"

BLOCKCHAIN_API = 'https://blockchain.info'
GETBLOCKCOUNT_URL =  BLOCKCHAIN_API + '/q/getblockcount'
DB_BLOCKCHAIN = 'local_blockchain.db'
PREVIOUS_BLOCKS = 1000

BICOIN_CORE_v3 = '3'
BICOIN_CORE_v4 = '4'
BITCOIN_XT = '536870919'

VERSION_BLOCK = {
    BICOIN_CORE_v3: "Bitcoin Core v3",
    BICOIN_CORE_v4: "Bitcoin Core v4",
    BITCOIN_XT: 'Bitcoin XT'
}

parser = argparse.ArgumentParser(description="List blocks version.")

parser.add_argument('--list-BIP101', action='store_true',
        help='List all the BIP101 blocks and their hashes')

parser.add_argument('--version', '-v', action='store_true',
        help='Show version')

args = parser.parse_args()

if args.version:
    print('Version ' + __version__)
    exit(0)


conn = sqlite3.connect(DB_BLOCKCHAIN)

c = conn.cursor()

def create_table():
    sql_str = "select name from sqlite_master"
    sql_str += " where type = 'table' and name = 'blockchain'"

    blockchain_table = c.execute(sql_str)

    if len(blockchain_table.fetchall()) == 0:
        sql_str = "create table blockchain (block int, version int, hash text)"
        c.execute(sql_str)

def get_highest_block():
    highest_block = read_url(GETBLOCKCOUNT_URL)

    return int(highest_block)

def get_latest_block():
    block = get_highest_block() - PREVIOUS_BLOCKS

    return block

def get_latest_fetched_block():
    sql_str = 'select block from blockchain order by block desc limit 1'
    sql = c.execute(sql_str)
    fetch = sql.fetchone()

    if fetch is None:
        return get_highest_block() - 1001

    return fetch[0] + 1

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
        print('Error trying to read: ' + url +\
        ' / Try to open in a browser to see what the error is.')
        sys.exit(0)

def insert_blocks(block):
    for i in range(block, get_highest_block() + 1):
        block_info = json.loads(read_url(BLOCK_INDEX_URL.format(str(i))))

        block_version = block_info['version']
        block_hash = block_info['hash']

        insert_sql = "INSERT INTO blockchain (block, version, hash) values "
        insert_sql += " (" + str(i) + ", "
        insert_sql += str(block_version) + ", "
        insert_sql += "'" + block_hash + "'"
        insert_sql += ")"

        c.execute(insert_sql)

        bi = block_version

        if str(bi) in VERSION_BLOCK.keys():
            print('Get block: ' + str(i) + ' - version: '\
            + VERSION_BLOCK[str(bi)])
        else:
            print('Get block: ' + str(i) +\
            ' - block version: unknown: ' + str(bi))

    conn.commit()

def show_block_summary():
    sql_str = "select version, count(version) as ver from "
    sql_str += " (select * from blockchain order by block desc limit 1000) "
    sql_str += " group by version"
    result = c.execute(sql_str)

    print("\nLatest: " + str(PREVIOUS_BLOCKS)+ " blocks\n")
    for i in result:
        if str(i[0]) in VERSION_BLOCK.keys():
            print(str(i[1]) + " mined with " + VERSION_BLOCK[str(i[0])])
        else:
            print(str(i[1]) + " mined with unknown version")


    print("\n")

def show_BIP101_blocks():
    sql_str = 'select hash from '
    sql_str += '(select * from blockchain order by block desc limit 1000) '
    sql_str += ' where version = ' + BITCOIN_XT

    result = c.execute(sql_str)

    print('Hashes of the BIP101 blocks: ')

    for i in result:
        print(str(i[0]))

create_table()

if args.list_BIP101:
    show_BIP101_blocks()

else:
    get_latest_block()
    get_latest_fetched_block()
    insert_blocks(set_block())

    show_block_summary()

conn.close()

