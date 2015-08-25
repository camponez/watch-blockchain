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

import json
import urllib2
import sqlite3

previous_blocks = 1000

conn = sqlite3.connect('local_blockchain.db')

c = conn.cursor()

is_there_table = c.execute("select name from sqlite_master where type = 'table' and name = 'blockchain'")

if len(is_there_table.fetchall()) == 0:
    c.execute("create table blockchain (block int, version int, hash text)")


highest_block = urllib2.urlopen('https://blockchain.info/q/getblockcount').read()

def get_hightest_block():
    block = int(highest_block) - previous_blocks

    return block

def get_latest_fetched_block():
    sql = c.execute('select block from blockchain order by block desc limit 1')
    return sql.fetchone()[0] + 1


#exit(0);

if len(c.execute("select * from blockchain").fetchall()) == 0:
    block = get_hightest_block()
else:
    block = get_latest_fetched_block()


block_api = 'https://blockexplorer.com/api'
block_index_url = block_api + '/block-index/'
block_url = block_api + '/block/'


for i in range(block, int(highest_block)):
    block_hash = json.load(urllib2.urlopen(block_index_url + str(i)))

    block_info = json.load(urllib2.urlopen(block_url + block_hash['blockHash']))

    insert_sql = "INSERT INTO blockchain (block, version, hash) values "
    insert_sql += " (" + str(i) + ", "
    insert_sql += str(block_info['version']) + ", "
    insert_sql += "'" + block_hash['blockHash'] + "'"
    insert_sql += ")"

    c.execute(insert_sql)
    print 'Inserted block: ' + str(i)


conn.commit()

c = c.execute("select version, count(version) as ver from (select * from blockchain order by block desc limit 1000) group by version")

version_block = {
    '3': "Bitcoin Core",
    '536870919': 'Bitcoin XT'
}

print "\nLatest: " + str(previous_blocks)+ " blocks\n"
for i in c:
    if str(i[0]) in version_block.keys():
        print str(i[1]) + " mined with " + version_block[str(i[0])]
    else:
        print str(i[1]) + " mined with unknown version"


print "\n"
conn.close()


