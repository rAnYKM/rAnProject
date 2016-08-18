# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

""" snapdb.py - SNAP data set to MySQL data base

Google+ Data Set

"""

from randb import rAnDB


def test_code():
    db = rAnDB('142.104.81.176', 3306, 'root', 'jychen21', 'ranproject')
    col = [
        rAnDB.col_gen('id', 'int', None, True, True),
        rAnDB.col_gen('name', 'varchar', 255, True),
        rAnDB.col_gen('city', 'varchar', 255),
        rAnDB.col_gen('age', 'int', None)
    ]
    names = ['name', 'city', 'age']
    values = ['jason', 'Shanghai', 24]
    db.new_table('test', col, 0)
    db.insert('test', names, values)
    db.insert('test', names, values)
    db.fetch_all('test', 2)
    db.connection.close()

if __name__ == '__main__':
    test_code()