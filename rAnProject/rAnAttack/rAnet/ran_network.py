# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

"""

rAnAttack.rAnet
    -- ran_network.py

ran_network VS ran_graph

- ran_network uses Graph_Tool package while ran_graph uses NetworkX regardless of what the names imply

"""
import logging
import numpy as np
import pandas as pd
import graph_tool.all as gt
from rAnProject.SNAPdata.GooglePlus.gp_network import GPEgoNetwork

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Ran Network Constants (alias)
# Node Table
NODE_ID = 'user_id'
NODE_PROFILE = 'profile'

# Feat Table
FEAT_ID = 'attr'
FEAT_CATEGORY = 'category'

# Edge Table
EDGE_SOURCE = 'start'
EDGE_TARGET = 'end'

# Link Table
LINK_USER = 'user_index'
LINK_FEAT = 'feat_index'


class Ranet:
    """
    NOTE: Ranet is designed to analyze a static network. PLEASE AVOID ADDING NODES BY GRAPH_TOOL API. Also, it is
    NOT RECOMMENDED to add nodes because of the low efficiency.
    Ranet includes at least the following 4 parts:
    1. node_table
    2. edge_table/relation_table (optional)
    3. feat_table/attribute_table
    4. link_table/attribute_link_table (optional)
    which is similar with RanGraph
    1,2 are included in social network (Ranet.network)
    3,4 are included in attribute network (Ranet.attr_network)

    - node_table
    user_id: string | profile: string

    - feat_table
    attr: string | category: string

    G = (V_N, V_A, E_N, E_A)
    attr_network G_A: [V] index 0 ~ |V_N|-1 -> V_N; index |V_N| ~ |V_N|+|V_A|-1 -> V_A

    Node feat consistency test
    >>> ego = Ranet()
    >>> ego.load_network_from_snap_gp('111213696402662884531')
    >>> ego.raw_check('111213696402662884531')
    True

    Build a new Ranet
    >>> ran = Ranet()
    >>> ran.add_node('ram', [('ram', 'name'), ('red', 'color')])
    >>> ran.add_node('rem', [('rem', 'name'), ('blue', 'color')], [('ram', 'rem')])
    >>> ran.get_node_feat(ran.aux_node_dict['rem'])
    [2, 3]
    >>> ran.add_node('emt', [('emt', 'name'), ('white', 'color')], [('rem', 'emt'), ('ram', 'emt')])
    >>> [ran.get_node_feat(ran.network.vertex_index[v], False, True) for v in ran.network.vertex(1).all_neighbours()]
    [[4, 5], [0, 1]]
    """
    def attr_index_g2t(self, index, graph_to_table=True):
        """
        Index Transform from Graph to Table or Table to Graph
        :param index: int
        :param graph_to_table: bool
        :return: int
        """
        return index - self.network.num_vertices() if graph_to_table else index + self.network.num_vertices()

    def load_network_from_snap_gp(self, ego):
        gp_ego = GPEgoNetwork(ego)
        self.network = gp_ego.network
        self.attr_network = gp_ego.attr_network
        self.node_table = gp_ego.node_table
        self.edge_table = gp_ego.relation_table
        self.feat_table = gp_ego.feat_table
        self.link_table = gp_ego.link_table
        self.aux_node_dict = gp_ego.aux_node_dict
        self.aux_feat_dict = gp_ego.aux_feat_dict

    def get_node_feat(self, index, is_sorted=False, graph_mode=True):
        """
        get a node feat list (index for feat_table).
        If is_sorted is True, the feature list will be sorted.
        If graph_mode is True, the feature is obtained from node_table (pd.DataFrame)
        :param index: int
        :param is_sorted: bool
        :param graph_mode: bool
        :return: list
        """
        if graph_mode:
            indices = [self.attr_index_g2t(self.attr_network.vertex_index[v])
                       for v in self.attr_network.vertex(index).all_neighbours()]
        else:
            profile = self.node_table[NODE_PROFILE][index]
            if profile is np.nan:
                indices = []
            else:
                indices = [int(val) for val in profile.split(' ')]
        if is_sorted:
            return sorted(indices)
        else:
            return indices

    def raw_check(self, ego):
        """
        Test the consistency of attribute network and raw data information
        :param ego: string
        :return: bool
        """
        from rAnProject.SNAPdata.GooglePlus.raw_loader import GPCSV2EgoLoader
        test_ego = GPCSV2EgoLoader(ego)
        for uid, feat in test_ego.node_table.values:
            index = self.aux_node_dict[uid]
            cmp_feat = self.get_node_feat(index, True)
            if feat is np.nan:
                if cmp_feat:
                    return False
                else:
                    continue
            else:
                indices = [int(attr) for attr in feat.split(' ')]
                if indices != cmp_feat:
                    print indices, self.get_node_feat(index, True)
                    return False
        return True

    def __renew_attribute_network(self):
        network = gt.Graph(directed=False)
        network.add_vertex(len(self.aux_node_dict.keys()) + len(self.aux_feat_dict.keys()))
        edge_list = [(link[0], link[1] + len(self.aux_node_dict.keys())) for link in self.link_table.values]
        network.add_edge_list(edge_list)
        self.attr_network = network

    def add_node(self, uid, attr_list=None, edge_list=None):
        """
        Add a social node (actor) into network
        :param uid: string
        :param attr_list: list (tuple: (attr, category))
        :param edge_list: list (string, string)
        :return: None
        """
        self.aux_node_dict[uid] = len(self.aux_node_dict.keys())
        self.network.add_vertex()

        if attr_list is None:
            self.node_table = self.node_table.append({NODE_ID: uid, NODE_PROFILE: np.nan},
                                                     ignore_index=True)
        else:
            attr_indices = []
            for attr in attr_list:
                if attr not in self.aux_feat_dict:
                    self.add_feat(attr[0], attr[1])
                attr_index = self.aux_feat_dict[attr[1] + ':' + attr[0]]
                self.link_table = self.link_table.append({LINK_USER: self.aux_node_dict[uid], LINK_FEAT: attr_index},
                                                         ignore_index=True)
                attr_indices.append(attr_index)
            self.node_table = self.node_table.append({NODE_ID: uid, NODE_PROFILE: ' '.join([str(attr)
                                                                                            for attr in attr_indices])},
                                                     ignore_index=True)
            self.__renew_attribute_network()

        if edge_list is not None:
            for edge in edge_list:
                neighbor = edge[0] if edge[1] == uid else edge[1]
                if neighbor not in self.aux_node_dict:
                    logging.debug('Node #%s does not exist, skipped' % neighbor)
                    continue
                else:
                    e0 = self.aux_node_dict[edge[0]]
                    e1 = self.aux_node_dict[edge[1]]
                    self.edge_table.append({EDGE_SOURCE: e0, EDGE_TARGET: e1}, ignore_index=True)
                    self.network.add_edge(self.network.vertex(e0), self.network.vertex(e1))

    def add_feat(self, feat, category):
        """
        Add an attribute node into attr_network
        :param feat: string
        :param category: string
        :return: None
        """
        self.feat_table = self.feat_table.append({FEAT_ID: feat, FEAT_CATEGORY: category},
                                                 ignore_index=True)
        self.attr_network.add_vertex()
        self.aux_feat_dict[category + ':' + feat] = len(self.aux_feat_dict.keys())

    def node_similarity(self, u, v):
        """
        Calculate the node similarity between u and v (index)
        :param u: int
        :param v: int
        :return: float
        """
        # Common attributes
        feat_u = set(self.get_node_feat(u))
        feat_v = set(self.get_node_feat(v))
        return len(feat_u & feat_v)/float(len(feat_u | feat_v) + 1)

    def __init__(self, is_directed=True):
        self.is_directed = is_directed
        self.network = gt.Graph(directed=is_directed)
        self.attr_network = gt.Graph(directed=False)
        self.node_table = pd.DataFrame(columns=[NODE_ID, NODE_PROFILE])
        self.edge_table = pd.DataFrame(columns=[EDGE_SOURCE, EDGE_TARGET])
        self.aux_node_dict = dict()
        self.feat_table = pd.DataFrame(columns=[FEAT_ID, FEAT_CATEGORY])
        self.link_table = pd.DataFrame(columns=[LINK_USER, LINK_FEAT])
        self.aux_feat_dict = dict()
