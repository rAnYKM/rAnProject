# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

"""

SNAPdata.GooglePlus
    -- gp_network.py

requirements:
    -- graph-tool

"""
import time
import logging
import numpy as np
import pandas as pd
import graph_tool.all as gt
import rAnProject.SNAPdata.GooglePlus.raw_loader as ld
from tables import COLUMNS


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class GPEgoNetwork(ld.GPCSV2EgoLoader):
    def __build_ego_network(self):
        t0 = time.time()
        network = gt.Graph(directed=True)
        network.add_vertex(len(self.aux_node_dict.keys()))
        # e_list = [(row[COLUMNS['edges'][0]], row[COLUMNS['edges'][1]])
        #           for index, row in self.relation_table.iterrows()]
        edges = [(row[COLUMNS['edges'][0]], row[COLUMNS['edges'][1]])
                 for index, row in self.relation_table.iterrows()]
        network.add_edge_list(edges)
        logging.debug('[Graph-tool] build network in %fs' % (time.time() - t0))
        # state = gt.minimize_blockmodel_dl(network)
        # state.draw(vertex_shape=state.get_blocks(), output="jason.pdf")
        return network

    def __build_attr_network(self):
        t0 = time.time()
        network = gt.Graph(directed=False)
        network.add_vertex(len(self.aux_node_dict.keys()) + len(self.aux_feat_dict.keys()))
        edge_list = [(row[COLUMNS['links'][0]], row[COLUMNS['links'][1]] + len(self.aux_node_dict.keys()))
                     for index, row in self.link_table.iterrows()]
        network.add_edge_list(edge_list)
        logging.debug('[Graph-tool] build attribute network in %fs' % (time.time() - t0))
        # state = gt.minimize_nested_blockmodel_dl(network, deg_corr=True)
        return network

    def get_link_table(self):
        """
        Get the attribute link table
        :return: pd.DataFrame
        """
        link_list = list()  # link_list is a list of dict
        profiles = self.node_table[COLUMNS['nodes'][1]]
        for index, profile in profiles.iteritems():
            # Parse the profile
            if profile is np.nan:
                continue
            else:
                feat_indexes = profile.split(' ')
                for feat_index in feat_indexes:
                    link_list.append({COLUMNS['links'][0]: index,
                                      COLUMNS['links'][1]: int(feat_index)})
        return pd.DataFrame(link_list)

    def get_relation_table(self):
        """
        relation_table only uses index but not uid
        :return: pd.DataFrame
        """
        relations = [{COLUMNS['edges'][0]: self.aux_node_dict[value[0]],
                      COLUMNS['edges'][1]: self.aux_node_dict[value[1]]}
                     for value in self.edge_table.values]
        """
        for i in self.edge_table.value:
            relations.append({COLUMNS['edges'][0]: self.aux_node_dict[self.edge_table[COLUMNS['edges'][0]][i]],
                             COLUMNS['edges'][1]: self.aux_node_dict[self.edge_table[COLUMNS['edges'][1]][i]]})
        """
        return pd.DataFrame(relations)

    def __init__(self, ego):
        ld.GPCSV2EgoLoader.__init__(self, ego)
        t0 = time.time()
        self.aux_node_dict, self.aux_feat_dict = self.get_aux_dict()
        self.link_table = self.get_link_table()
        self.relation_table = self.get_relation_table()
        logging.debug('[gp_network] Make tables in %fs' % (time.time() - t0))
        self.network = self.__build_ego_network()
        self.attr_network = self.__build_attr_network()
