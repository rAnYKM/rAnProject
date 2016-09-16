# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

"""

SNAPdata.GooglePlus
    -- raw_loader.py

"""
import ranfig as rfg
import pandas as pd
import time
import logging
from SNAPdata.GooglePlus.tables import *

Base = declarative_base()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class SnapRawGPLoader:
    def get_ego_net(self, uid):
        t0 = time.time()
        node_table = pd.read_sql_query('SELECT * '
                                       'FROM nodes '
                                       'WHERE nodes.root = %s' %uid, self.engine)
        edge_table = pd.read_sql_query('SELECT * '
                                       'FROM edges '
                                       'WHERE edges.root = %s' % uid, self.engine)
        attr_table = pd.read_sql_query('SELECT * '
                                       'FROM attributes '
                                       'WHERE attributes.root = %s' % uid, self.engine)
        logging.debug('Ego Network #%s Loaded in %f s' % (uid, time.time() - t0))
        return node_table, edge_table, attr_table

    def __init_db(self):
        self.engine = init_database_from_ranfig(self.ranfig, 'GooglePlus')

    def __init__(self, ranfig_dir=RANFIG_DIR):
        self.ranfig = ranfig_dir
        self.__init_db()

def main():
    sgp = SnapRawGPLoader()
    print sgp.get_ego_net('115516333681138986628')[1].count()

if __name__ == '__main__':
    main()