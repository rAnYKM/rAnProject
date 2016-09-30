# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

"""

SNAPdata.GooglePlus
    -- rangp.py

"""
import os
import pandas as pd
import rAnProject.ranfig as rfg
import rAnProject.settings as settings


RAN_GP_NAME = 'googleplus'
FEAT_NAME_DICT = {'rnd': 0, 'mns': 1, 'exe': 2}
FEAT_NAMES = ['rnd', 'mns', 'exe']


class RanGPNet:
    def __raw_loader(self, ranfig_dir=settings.SETTINGS_DIR):
        dirs = rfg.load_ranfig(ranfig_dir)['SNAP']['rangp']
        edge_table = pd.read_csv(os.path.join(dirs, RAN_GP_NAME + '-edges.csv'))
        node_table = pd.read_csv(os.path.join(dirs, RAN_GP_NAME + '-nodes.csv'))
        return node_table, edge_table

    def __feat_table(self):
        feat_table = pd.DataFrame([{'attr': feat, 'category': 'class'} for feat in FEAT_NAMES])
        tmp_table = pd.DataFrame(self.node_table)
        for index, profile in self.node_table['profile'].iteritems():
            tmp_table['profile'][index] = FEAT_NAME_DICT[profile]
        return feat_table, tmp_table

    def __init__(self, ranfig_dir=settings.SETTINGS_DIR):
        self.node_table, self.edge_table = self.__raw_loader(ranfig_dir)
        self.feat_table, self.node_table = self.__feat_table()
