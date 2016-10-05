# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

"""

SNAPdata.GooglePlus
    -- rangp.py

"""
import os
import time
import logging
import pandas as pd
import graph_tool.all as gt
import rAnProject.ranfig as rfg
import rAnProject.settings as settings

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
RAN_GP_NAME = 'googleplus'
FEAT_NAME_DICT = {'rnd': 0, 'mns': 1, 'exe': 2}
FEAT_NAMES = ['rnd', 'mns', 'exe']


class RanGPNet:
    def get_aux_dict(self):
        """
        Get the auxiliary node and feature dictionary
        uid -> index
        category: feature -> index
        :return: dict, dict
        """
        nodes = self.node_table['uid']
        feats = [value[1] + ':' + str(value[0])
                 for value in self.feat_table.values]
        return {node: index for index, node in nodes.iteritems()}, {feat: index for index, feat in enumerate(feats)}

    def __raw_loader(self, ranfig_dir=settings.SETTINGS_DIR):
        dirs = rfg.load_ranfig(ranfig_dir)['SNAP']['rangp']
        edge_table = pd.read_csv(os.path.join(dirs, RAN_GP_NAME + '-edges.csv'))
        node_table = pd.read_csv(os.path.join(dirs, RAN_GP_NAME + '-nodes.csv'))
        return node_table, edge_table

    def __clean_edge_table(self):
        tmp_list = [{'start': start, 'end': end} for start, end in self.edge_table.values
                    if start in self.aux_node_dict and end in self.aux_node_dict]
        return pd.DataFrame(tmp_list)

    def __feat_table(self):
        feat_table = pd.DataFrame([{'attr': feat, 'category': 'class'} for feat in FEAT_NAMES])
        tmp_table = pd.DataFrame(self.node_table)
        for index, profile in self.node_table['profile'].iteritems():
            tmp_table['profile'][index] = FEAT_NAME_DICT[profile]
        return feat_table, tmp_table

    def __link_table(self):
        link_dict = [{'user_id': self.aux_node_dict[uid], 'attr': feat} for uid, feat in self.node_table.values]
        return pd.DataFrame(link_dict)

    def __build_ego_network(self):
        t0 = time.time()
        network = gt.Graph(directed=True)
        network.add_vertex(len(self.aux_node_dict.keys()))
        # e_list = [(row[COLUMNS['edges'][0]], row[COLUMNS['edges'][1]])
        #           for index, row in self.relation_table.iterrows()]
        network.add_edge_list(self.relation_table.values)
        logging.debug('[Graph-tool] build network in %fs' % (time.time() - t0))
        # state = gt.minimize_blockmodel_dl(network)
        # state.draw(vertex_shape=state.get_blocks(), output="jason.pdf")
        return network

    def __build_attr_network(self):
        t0 = time.time()
        network = gt.Graph(directed=False)
        network.add_vertex(len(self.aux_node_dict.keys()) + len(self.aux_feat_dict.keys()))
        edge_list = [(e[0] + len(self.aux_node_dict.keys()), e[1]) for e in self.link_table.values]
        network.add_edge_list(edge_list)
        logging.debug('[Graph-tool] build attribute network in %fs' % (time.time() - t0))
        # state = gt.minimize_nested_blockmodel_dl(network, deg_corr=True)
        # gt.draw_hierarchy(state, output="jason.pdf")
        return network

    def get_relation_table(self):
        """
        relation_table only uses index but not uid
        :return: pd.DataFrame
        """
        relations = [{'start': self.aux_node_dict[value[0]],
                      'end': self.aux_node_dict[value[1]]}
                     for value in self.edge_table.values]
        return pd.DataFrame(relations)

    def __init__(self, ranfig_dir=settings.SETTINGS_DIR):
        self.node_table, self.edge_table = self.__raw_loader(ranfig_dir)
        self.feat_table, self.node_table = self.__feat_table()
        self.aux_node_dict, self.aux_feat_dict = self.get_aux_dict()
        self.link_table = self.__link_table()
        self.edge_table = self.__clean_edge_table()
        self.relation_table = self.get_relation_table()
        self.network = self.__build_ego_network()
        self.attr_network = self.__build_attr_network()
