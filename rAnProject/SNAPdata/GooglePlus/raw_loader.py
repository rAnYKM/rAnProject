# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

"""

SNAPdata.GooglePlus
    -- raw_loader.py

"""
import logging
import os
import re
import time

import numpy as np
import pandas as pd
from SNAPdata.GooglePlus.tables import *

from build_raw_database import get_ego_nodes
from rAnProject import ranfig as rfg

Base = declarative_base()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

NONSENSE_SUFFIX = ['inc', 'com', 'corporation']


class SnapRawGPLoader:
    def get_ego_net(self, uid):
        t0 = time.time()
        self.__init_db()
        node_table = pd.read_sql_query('SELECT * '
                                       'FROM nodes '
                                       'WHERE nodes.root = %s' % uid, self.engine)
        edge_table = pd.read_sql_query('SELECT * '
                                       'FROM edges '
                                       'WHERE edges.root = %s' % uid, self.engine)
        attr_table = pd.read_sql_query('SELECT * '
                                       'FROM attributes '
                                       'WHERE attributes.root = %s' % uid, self.engine)
        logging.debug('Ego Network #%s Loaded in %f s' % (uid, time.time() - t0))
        return node_table, edge_table, attr_table

    def csv_ego_net(self, uid):
        t0 = time.time()
        dirs = rfg.load_ranfig(self.ranfig)['SNAP']['googleplus']
        node_table = pd.read_csv(os.path.join(dirs, 'csv', uid + '-node.csv'))
        edge_table = pd.read_csv(os.path.join(dirs, 'csv', uid + '-edge.csv'))
        attr_table = pd.read_csv(os.path.join(dirs, 'csv', uid + '-feat.csv'))
        logging.debug('Ego Network #%s Loaded in %f s' % (uid, time.time() - t0))
        return node_table, edge_table, attr_table

    def __init_db(self):
        self.engine = init_database_from_ranfig(self.ranfig, 'GooglePlus')

    def __init__(self, ranfig_dir=RANFIG_DIR):
        self.ranfig = ranfig_dir
        self.egos = get_ego_nodes()


class GPRawEgoLoader(SnapRawGPLoader):
    @staticmethod
    def clean_string(st):
        word = "_".join(re.findall("[a-zA-Z0-9]+", st)).lower()
        word = re.sub('_(%s)$' % '|'.join(NONSENSE_SUFFIX), '', word)
        return word

    def get_feat(self, index):
        name = self.feat_table[COLUMNS['attributes'][0]][index]
        cate = self.feat_table[COLUMNS['attributes'][1]][index]
        return cate + ':' + self.clean_string(str(name))

    def get_new_feat(self, index):
        name = self.new_feat_table[COLUMNS['attributes'][0]][index]
        cate = self.new_feat_table[COLUMNS['attributes'][1]][index]
        return cate + ':' + name

    def gen_node_table(self):
        tmp_node_table = pd.DataFrame(self.node_table)
        profiles = tmp_node_table[COLUMNS['nodes'][1]]
        for index, profile in profiles.iteritems():
            attr_indexes = [i for i, attr in enumerate(profile.split(' '))
                            if attr == '1']
            feats = '|'.join([self.get_feat(i) for i in attr_indexes])
            if not feats:
                feats = np.nan
            tmp_node_table[COLUMNS['nodes'][1]][index] = feats
        return tmp_node_table

    def gen_feat_table(self, node_table):
        feats = set()
        for profile in node_table[COLUMNS['nodes'][1]][self.node_table.profile.notnull()]:
            feat = profile.split('|')
            for f in feat:
                if f.split(':')[1] != '':
                    feats.add(f)
        feats = [{COLUMNS['attributes'][0]: f.split(':')[1],
                  COLUMNS['attributes'][1]: f.split(':')[0]}
                 for f in feats]
        new_feats = sorted(list(feats), key=lambda fe: (fe[COLUMNS['attributes'][1]],
                                                        fe[COLUMNS['attributes'][0]]))
        aux_feat_dict = {feat[COLUMNS['attributes'][1]] + ':' + feat[COLUMNS['attributes'][0]]: i
                         for i, feat in enumerate(new_feats)}
        new_feat_table = pd.DataFrame(new_feats)
        return new_feat_table, aux_feat_dict

    def write_new_csv(self):
        new_index_node_table = pd.DataFrame(self.new_node_table)
        for index, profile in enumerate(new_index_node_table[COLUMNS['nodes'][1]]):
            if profile is np.nan:
                continue
            else:
                feat = profile.split('|')
                new_profile = set()
                for f in feat:
                    row = f.split(':')
                    if row[1] != '':
                        index_feat = self.aux_feat_dict[f]
                        new_profile.add(index_feat)
                        # index_feat = self.new_feat_table[
                        #     (self.new_feat_table[COLUMNS['attributes'][1]] == row[0]) & (
                        #     self.new_feat_table[COLUMNS['attributes'][0]] == row[1])].index.tolist()
                        # new_profile.add(index_feat[0])
                # print profile
                new_profile_li = sorted(new_profile)
                # print '|'.join([self.get_new_feat(p) for p in new_profile_li])
                new_profile_str = ' '.join([str(i) for i in new_profile_li])
                new_index_node_table[COLUMNS['nodes'][1]][index] = new_profile_str
        # print self.new_index_node_table
        rfg_settings = rfg.load_ranfig(self.ranfig)
        dirs = rfg_settings['SNAP']['googleplus']
        if not os.path.exists(os.path.join(dirs, 'csv_v2')):
            os.makedirs(os.path.join(dirs, 'csv_v2'))
        self.new_node_table.to_csv(os.path.join(dirs, 'csv_v2', self.ego + '-node.csv'), index=False)
        self.new_feat_table.to_csv(os.path.join(dirs, 'csv_v2', self.ego + '-feat.csv'), index=False)
        self.edge_table.to_csv(os.path.join(dirs, 'csv_v2', self.ego + '-edge.csv'), index=False)

    def __init__(self, ego, ranfig_dir=RANFIG_DIR, csv_mode=True):
        SnapRawGPLoader.__init__(self, ranfig_dir)
        if ego not in self.egos:
            raise ValueError('Ego Network #%s does not exist.' % ego)
        self.ego = ego
        if csv_mode:
            self.node_table, self.edge_table, self.feat_table = self.csv_ego_net(ego)
        else:
            self.node_table, self.edge_table, self.feat_table = self.get_ego_net(ego)
        self.new_node_table = self.gen_node_table()
        self.new_feat_table, self.aux_feat_dict = self.gen_feat_table(self.new_node_table)


class GPCSV2EgoLoader:
    def get_aux_dict(self):
        """
        Get the auxiliary node and feature dictionary
        uid -> index
        category: feature -> index
        :return: dict, dict
        """
        nodes = self.node_table[COLUMNS['nodes'][0]]
        print self.feat_table
        feats = [value[1] + ':' + str(value[0])
                 for value in self.feat_table.values]
        return {node: index for index, node in nodes.iteritems()}, {feat: index for index, feat in enumerate(feats)}

    def __init__(self, ego, ranfig_dir=RANFIG_DIR):
        self.ranfig = ranfig_dir
        self.egos = get_ego_nodes()
        if ego not in self.egos:
            raise ValueError('Ego Network #%s does not exist.' % ego)
        self.ego = ego
        dirs = rfg.load_ranfig(self.ranfig)['SNAP']['googleplus']
        t0 = time.time()
        self.node_table = pd.read_csv(os.path.join(dirs, 'csv_v2', self.ego + '-node.csv'))
        self.edge_table = pd.read_csv(os.path.join(dirs, 'csv_v2', self.ego + '-edge.csv'))
        self.feat_table = pd.read_csv(os.path.join(dirs, 'csv_v2', self.ego + '-feat.csv'))
        logging.debug('Ego Network #%s Loaded in %f s' % (self.ego, time.time() - t0))


def generate_csv_v2():
    """
    Generate the csv list of simply formatted data
    :return: none
    """
    li = get_ego_nodes()
    for index, ego in enumerate(li):
        t0 = time.time()
        ego_net = GPRawEgoLoader(ego)
        ego_net.write_new_csv()
        logging.debug('Finish adding No.%d ego network #%s in %fs' % (index, ego, time.time() - t0))


if __name__ == '__main__':
    pass
