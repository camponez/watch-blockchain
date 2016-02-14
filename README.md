Description
===========

This script is to track the latest 1000 blocks from the Bitcoin Blockchain and
show blocks per version.

Usage
=====
`python BIP101.py`

A sqlite3 will be create and it will load the latest 1000 blocks. It might take
a while.

To update, just run again and only the blocks that are not in the database will
be updated.

Options
=======

```
-h, --help     show this help message and exit
--list-BIP101  List all the BIP101 blocks and their hashes
--list-classic  List all the Classic blocks and their hashes
--last LAST    Show lastest blocks
--quiet        Don't show messages!
--version, -v  Show version`
```
Contribution
===========
If you would like to contribute send your push request.

If you like to donate: [19kTizUhnoCqofijNX5xPmGKmjDpz2hBMF](https://blockchain.info/address/19kTizUhnoCqofijNX5xPmGKmjDpz2hBMF)

