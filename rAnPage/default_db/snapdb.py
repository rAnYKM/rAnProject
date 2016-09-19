# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

""" snapdb.py - SNAP data set to MySQL data base

SNAP Google+ & Facebook Data Set

"""

import os
import ranfig as rfg
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import time
import logging
from module_facebook import Nodes, Attributes, Relations, AttributeLinks

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
Base = declarative_base()


class SnapFacebook:
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
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    def __core_insert_node_list(self):
        t0 = time.time()
        self.engine.execute(
            Nodes.__table__.insert(),
            [{'user_id': node_name} for node_name in self.node.keys()]
        )
        logging.debug('SQLAlchemy Core: Insert node list in %f s' % (time.time() - t0))

    def __dict_for_attr_insert(self, attr, cate, max_cate_number=3):
        res_dict = {'attr_id': 'a' + self.__abbr_attr(cate) + attr}
        for cno, c in enumerate(cate):
            if cno >= max_cate_number:
                break
            else:
                res_dict['category_' + str(cno + 1)] = c
        for cno in range(len(cate), max_cate_number):
            res_dict['category_' + str(cno + 1)] = None
        return res_dict

    def __core_insert_attr_list(self):
        t0 = time.time()
        self.engine.execute(
            Attributes.__table__.insert(),
            [self.__dict_for_attr_insert(f[0], f[1]) for f in self.featname]
        )
        logging.debug('SQLAlchemy Core: Insert attribute list in %f s' % (time.time() - t0))

    def __core_insert_relation_list(self):
        t0 = time.time()
        large_edges = self.edges + [[self.root, node] for node in self.friends]
        self.engine.execute(
            Relations.__table__.insert(),
            [{'source': e[0], 'destination': e[1]} for e in large_edges]
        )
        logging.debug('SQLAlchemy Core: Insert social relation list in %f s' % (time.time() - t0))

    def __core_insert_link_list(self):
        t0 = time.time()
        large_links = []
        for n, fs in self.node.iteritems():
            large_links += [{'user': n, 'attr': 'a' + self.__abbr_attr(self.featname[att][1]) + self.featname[att][0]}
                            for att in fs]
        self.engine.execute(
            AttributeLinks.__table__.insert(),
            large_links
        )
        logging.debug('SQLAlchemy Core: Insert attribute link list in %f s' % (time.time() - t0))

    def __init__(self, ego_id):
        self.ranfig = rfg.load_ranfig('../../settings.ini')
        self.dir = self.ranfig['SNAP']
        self.root = ego_id
        self.featname = self.__feat_name_list()
        self.node = self.__node_feat_list()
        # Add Root Node Into Node List
        self.egofeat = self.__ego_feat_list()
        self.node[self.root] = self.egofeat
        self.edges, self.friends = self.__edge_list()
        self.__init_db()
        self.__core_insert_node_list()
        self.__core_insert_attr_list()
        self.__core_insert_relation_list()
        self.__core_insert_link_list()


if __name__ == '__main__':
    egonet = SnapFacebook('107')
