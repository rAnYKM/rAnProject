# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

""" randb.py - Basic Database Operations for MySQL

MySQL database access operations
Make SQL more Pythonic

Requirements:

- MySQLdb Package

"""

import sys
import MySQLdb as mysql
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class rAnDB:
    def __init__(self, host, port, user, password, db, charset="utf8"):
        """ Create a connection to MySQL Database
        :param host: string
        :param port: string
        :param user: string
        :param password: string
        :param db: string
        :param charset: string
        """
        try:
            self.connection = mysql.connect(host=host, port=port, user=user, passwd=password, db=db, charset=charset)
            self.cursor = self.connection.cursor()
        except mysql.Error, e:
            logging.error('Error %d: %s' % (e.args[0], e.args[1]))
            sys.exit(1)

    @staticmethod
    def col_gen(name, mtype, msize, not_null=False, auto_increment=False):
        if msize is not None:
            msize = str(msize)
        tmp = {
            'name': name,
            'type': mtype,
            'size': msize,
            'not_null': not_null,
            'auto_increment': auto_increment,
        }
        return tmp

    def new_table(self, table_name, cols, key=-1):
        """ CREATE TABLE ...
        :param table_name: string
        :param cols: list(dict)
        :param key: int
        :return: bool
        """
        sub_sql = list()
        for col in cols:
            tmp_sql = col['name'] + ' ' + col['type']
            if col['size'] is not None:
                tmp_sql += '(' + col['size'] + ')'
            if col['not_null']:
                tmp_sql += ' NOT NULL'
            if col['auto_increment']:
                tmp_sql += ' AUTO_INCREMENT'
            sub_sql.append(tmp_sql)
        if 0 <= key < len(cols):
            sub_sql.append('PRIMARY KEY (%s)' % cols[key]['name'])
        sql = 'CREATE TABLE %s (%s)' % (table_name, ', '.join(sub_sql))
        logging.debug('SQL Executed: %s' % sql)
        self.cursor.execute(sql)

    def insert(self, table_name, names, values):
        new_values = []
        for v in values:
            # This is not pythonic :<
            if isinstance(v, str):
                new_values.append('\"%s\"' % v)
            else:
                new_values.append(str(v))
        sql = 'INSERT INTO %s (%s) VALUES(%s)' \
              % (table_name, ','.join(names), ','.join(new_values))
        logging.debug('SQL Executed: %s' % sql)
        self.cursor.execute(sql)
        self.connection.commit()

    def fetch_all(self, table_name, number):
        sql = "SELECT * FROM %s LIMIT %d" % (table_name, number)
        logging.debug('SQL Executed: %s' % sql)
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print row
