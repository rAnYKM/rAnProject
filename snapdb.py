# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

""" snapdb.py - SNAP data set to MySQL data base

Google+ Data Set

"""

import os
from randb import rAnDB
import ranfig as rfg
from sqlalchemy import create_engine, Column, Integer, String, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
Base = declarative_base()


def test_code2():
    ranfig = rfg.load_ranfig()
    database = ranfig['Database']
    engine = create_engine('%s://%s:%s@%s:%s/%s' %
                           (database['engine'], database['user'], database['password'],
                            database['host'], database['port'], database['db']))
    conn = engine.connect()
    result = conn.execute('SELECT * FROM test')
    for row in result:
        print row
    conn.close()


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
    # db.new_table('test', col, 0)
    # db.insert('test', names, values)
    # db.insert('test', names, values)
    print db.fetch_column_name('test')
    print db.simple_select('test')
    db.connection.close()


class SnapFacebook:
    class Nodes(Base):
        __tablename__ = 'nodes'
        id = Column(Integer, primary_key=True, autoincrement=True)
        user_id = Column(Integer, index=True, nullable=False)

    class Attributes(Base):
        __tablename__ = 'attributes'
        id = Column(Integer, primary_key=True, autoincrement=True)
        attr_id = Column(String(255), index=True, nullable=False)
        category_1 = Column(String(255))
        category_2 = Column(String(255))
        category_3 = Column(String(255))

    class Relations(Base):
        __tablename__ = 'relations'
        id = Column(Integer, primary_key=True, autoincrement=True)
        source = Column(Integer, nullable=False)
        destination = Column(Integer, nullable=False)
        __table_args__ = (
            ForeignKeyConstraint(['source', 'destination'], ['nodes.uid', 'nodes.uid'])
        )

    class AttributeLinks(Base):
        __tablename__ = 'attribute_links'
        id = Column(Integer, primary_key=True, autoincrement=True)
        user = Column(Integer, nullable=False)
        attr = Column(String(255), nullable=False)
        __table_args__ = (
            ForeignKeyConstraint(['user', 'attr'], ['nodes.uid', 'attributes.uid'])
        )

    @staticmethod
    def __abbr_attr(attr):
        abbr_l = [a[0] + a[-1] for a in attr]
        return ''.join(abbr_l) + '-'

    @staticmethod
    def __feat_process(line):
        """
        Split the raw data into an attribute
        Example:
        '12 education;classes;id;anonymized feature 12
        -> 12, ['education', 'classes', 'id']
        :param line: String
        :return: feature number, feature root
        """
        fields = line.strip().split(';')
        feat_name = fields[-1].strip('').replace('anonymized feature ', '')
        fields[0] = fields[0].split(' ')[1]
        cate_list = fields[:-1]
        return feat_name, cate_list

    @staticmethod
    def __node_process(feat):
        """
        ID [Binary Feature Vector]
        :param feat: String
        :return: Dict
        """
        li = feat.strip('\r\n').split(' ')
        uid = li[0]
        fea = li[1:]
        index = [num for num, value in enumerate(fea) if value == '1']
        return uid, index

    def __feat_name_list(self):
        with open(os.path.join(self.dir['facebook'], self.root + '.featnames'), 'rb') as fp:
            feat_name = [self.__feat_process(line) for line in fp.readlines()]
            logging.debug('%d Feat(s) have been loaded.' % len(feat_name))
            return feat_name

    def __node_feat_list(self):
        with open(os.path.join(self.dir['facebook'], self.root + '.feat'), 'rb') as fp:
            nodes = [self.__node_process(feat) for feat in fp.readlines()]
            node_dict = dict(nodes)
            logging.debug('%d User Feature List(s) have been loaded.' % len(nodes))
            return node_dict

    def __ego_feat_list(self):
        with open(os.path.join(self.dir['facebook'], self.root + '.egofeat'), 'rb') as fp:
            li = fp.readline().strip('\r\n').split(' ')
            index = [num for num, value in enumerate(li) if value == '1']
            logging.debug('%d Ego Feature(s) have been loaded.' % len(index))
            return index

    def __edge_list(self):
        with open(os.path.join(self.dir['facebook'], self.root + '.edges'), 'rb') as fp:
            edges = []
            follows_set = set()
            for line in fp.readlines():
                pairs = line.strip().split(' ')
                edges.append(pairs)
                follows_set.add(pairs[0])
                follows_set.add(pairs[1])
            logging.debug('%d Edge(s) have been loaded.' % len(edges))
            logging.debug('%d Ego Friend(s) have been loaded.' % len(follows_set))
            return edges, list(follows_set)

    def __init_db(self):
        database = self.ranfig['Database']
        self.engine = create_engine('%s://%s:%s@%s:%s/%s' %
                               (database['engine'], database['user'], database['password'],
                                database['host'], database['port'], database['db']))
        self.conn = self.engine.connect()


    def __init__(self, ego_id):
        self.ranfig = rfg.load_ranfig()
        self.dir = self.ranfig['SNAP']
        self.root = ego_id
        self.featname = self.__feat_name_list()
        self.node = self.__node_feat_list()
        # Add Root Node Into Node List
        self.egofeat = self.__ego_feat_list()
        self.node[self.root] = self.egofeat
        self.edges, self.friends = self.__edge_list()


if __name__ == '__main__':
    test_code2()
