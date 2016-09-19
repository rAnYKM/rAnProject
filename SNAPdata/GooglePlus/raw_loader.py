# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

"""

SNAPdata.GooglePlus
    -- raw_loader.py

"""
import os
import re
import ranfig as rfg
import pandas as pd
import numpy as np
import time
import logging
from SNAPdata.GooglePlus.tables import *
from build_raw_database import get_ego_nodes


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

    def profile_change(self):
        profiles = self.node_table[COLUMNS['nodes'][1]]
        for index, profile in profiles.iteritems():
            attr_indexes = [i for i, attr in enumerate(profile.split(' '))
                            if attr == '1']
            feats = '|'.join([self.get_feat(i) for i in attr_indexes])
            if not feats:
                feats = np.nan
            self.node_table[COLUMNS['nodes'][1]][index] = feats
        print self.node_table

    def count_feat(self):
        feats = set()
        for profile in self.node_table[COLUMNS['nodes'][1]][self.node_table.profile.notnull()]:
            feat = profile.split('|')
            for f in feat:
                if f.split(':')[1] != '':
                    feats.add(f)
        feats = [{COLUMNS['attributes'][0]: f.split(':')[1],
                  COLUMNS['attributes'][1]: f.split(':')[0]}
                 for f in feats]
        new_feats = sorted(list(feats), key=lambda fe: (fe[COLUMNS['attributes'][1]],
                                                        fe[COLUMNS['attributes'][0]]))
        new_feat_table = pd.DataFrame(new_feats)
        print new_feat_table

    def __init__(self, ego, ranfig_dir=RANFIG_DIR, csv_mode=True):
        SnapRawGPLoader.__init__(self, ranfig_dir)
        if ego not in self.egos:
            raise ValueError('Ego Network #%s does not exist.' % ego)
        self.ego = ego
        if csv_mode:
            self.node_table, self.edge_table, self.feat_table = self.csv_ego_net(ego)
        else:
            self.node_table, self.edge_table, self.feat_table = self.get_ego_net(ego)


def main():
    ego = GPRawEgoLoader('100535338638690515335')
    print ego.feat_table
    ego.profile_change()
    ego.count_feat()


if __name__ == '__main__':
    main()
