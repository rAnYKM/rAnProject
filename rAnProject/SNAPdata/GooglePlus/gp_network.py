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
    def _build_ego_network(self):
        t0 = time.time()
        network = gt.Graph(directed=True)
        network.add_vertex(len(self.aux_node_dict.keys()))
        # e_list = [(row[COLUMNS['edges'][0]], row[COLUMNS['edges'][1]])
        #           for index, row in self.relation_table.iterrows()]
        network.add_edge_list(self.relation_table.values)
        logging.debug('[Graph-tool] build network in %fs' % (time.time() - t0))
        # TODO: graph node properties
        # Degree Properties
        in_degrees = network.new_vertex_property('int')
        out_degrees = network.new_vertex_property('int')
        degrees = network.new_vertex_property('int')
        has_degrees = network.new_vertex_property('bool')
        for v in network.vertices():
            in_degrees[v] = v.in_degree()
            out_degrees[v] = v.out_degree()
            degrees[v] = in_degrees[v] + out_degrees[v]
            has_degrees[v] = (degrees[v] != 0)
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
        self.network = self._build_ego_network()


def main():
    ego = GPEgoNetwork('100535338638690515335')
    # print ego.link_table
    # print ego.relation_table


if __name__ == '__main__':
    main()
