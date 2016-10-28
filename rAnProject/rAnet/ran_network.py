# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

"""

rAnet
    -- ran_network.py

ran_network VS ran_graph

- ran_network uses Graph_Tool package while ran_graph uses NetworkX regardless of what the names imply

"""
import logging
from collections import Counter
import numpy as np
import pandas as pd
import graph_tool.all as gt

from rAnProject.SNAPdata.GooglePlus.gp_network import GPEgoNetwork
from rAnProject.SNAPdata.Facebook.fb_loader import FacebookEgoNet
from rAnProject.SNAPdata.Sample.rangp import RanGPNet

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
    @staticmethod
    def get_density(graph, is_directed=True):
        nv = graph.num_vertices()
        ne = graph.num_edges()
        if is_directed:
            me = nv*(nv - 1)
        else:
            me = nv*(nv - 1)/2
        if me == 0:
            return 0
        return ne/float(me)

    def attr_index_g2t(self, index, graph_to_table=True):
        """
        Index Transform from Graph to Table or Table to Graph
        :param index: int
        :param graph_to_table: bool
        :return: int
        """
        return index - self.network.num_vertices() if graph_to_table else index + self.network.num_vertices()

    def load_network_from_snap(self, ego, snap='googleplus'):
        if snap == 'googleplus':
            ego_net = GPEgoNetwork(ego)
        else:
            ego_net = FacebookEgoNet(ego)
        self.network = ego_net.network
        self.attr_network = ego_net.attr_network
        self.node_table = ego_net.node_table
        self.edge_table = ego_net.relation_table
        self.feat_table = ego_net.feat_table
        self.link_table = ego_net.link_table
        self.aux_node_dict = ego_net.aux_node_dict
        self.aux_feat_dict = ego_net.aux_feat_dict

    def load_network_from_sample(self):
        gp_net = RanGPNet()
        self.network = gp_net.network
        self.attr_network = gp_net.attr_network
        self.node_table = gp_net.node_table
        self.edge_table = gp_net.relation_table
        self.feat_table = gp_net.feat_table
        self.link_table = gp_net.link_table
        self.aux_node_dict = gp_net.aux_node_dict
        self.aux_feat_dict = gp_net.aux_feat_dict
        self.is_directed = False
        self.network.set_directed(self.is_directed)

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

    def get_feat_node(self, index, is_sorted=False, graph_mode=True):
        """
        get a feature's neighbor node index (graph mode: the feat index in graph)
        :param index: int
        :param is_sorted: bool
        :param graph_mode: bool
        :return: list
        """
        if graph_mode:
            indices = [self.attr_network.vertex_index[v]
                       for v in self.attr_network.vertex(index).all_neighbours()]
        else:
            indices = [self.attr_network.vertex_index[v]
                       for v in self.attr_network.vertex(self.attr_index_g2t(index, False)).all_neighbours()]
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

    # Simple Analysis Tool
    def feature_rank(self, sel_feats, mode='common'):
        """
        Rank the most common features/attributes among social nodes with selected features/attributes by index
        Example of sel_feats:
        [(1, 3), (2, 4), (5,)]
        (set1 | set3) & (set2 | set4) & set5
        modes:
        - common (default): common neighbor number
        - jaccard: Jaccard coefficient
        - ada-node: Adamic/Adar score in network
        - ada-feat: Adamic/Adar score in attr_network
        - entropy: mutual information
        :param sel_feats: list
        :param mode: string
        :return: pd.DataFrame
        """
        universal_set = set(self.aux_node_dict.values())
        ex_feats = []
        for block in sel_feats:
            block_set = set(self.aux_node_dict.values())
            flag = False
            for feat in block:
                neighbors = set(self.get_feat_node(index=feat, graph_mode=False))
                if not flag:
                    block_set = neighbors
                    flag = True
                else:
                    block_set |= neighbors
                ex_feats.append(feat)
            universal_set &= block_set
        ranks = dict()
        for attr, num in self.aux_feat_dict.iteritems():
            if num in ex_feats:
                continue
            else:
                neighbors = set(self.get_feat_node(index=num, graph_mode=False))
                if mode == 'jaccard':
                    result = len(neighbors & universal_set)/float(len(neighbors | universal_set))
                elif mode == 'ada-node':
                    result = 0
                    for n in neighbors & universal_set:
                        result += 1 / (np.log2(len(list(self.network.vertex(n).out_neighbours())) + 1) + 1)
                elif mode == 'ada-feat':
                    result = 0
                    for n in neighbors & universal_set:
                        result += 1 / (np.log2(len(self.get_node_feat(n)) + 1) + 1)
                elif mode == 'entropy':
                    result = np.log2(len(neighbors & universal_set) / \
                             float(len(neighbors) + len(universal_set)) * \
                             len(self.aux_node_dict.values()))
                else:
                    result = len(neighbors & universal_set)
                if result > 0:
                    ranks[attr] = result
        return pd.DataFrame([{FEAT_ID: key, 'count': value} for key, value in ranks.iteritems()])

    def select_feat_by_name(self, name):
        col = self.feat_table[FEAT_ID]
        table = col.str.contains(name)
        return tuple(table[table==True].index)

    def original_block_model(self):
        state = gt.minimize_nested_blockmodel_dl(self.network, deg_corr=True)
        block_list = [self.__level_model(state, v, 0) for v in range(len(self.aux_node_dict.keys()))]
        return block_list, state

    def __level_model(self, state, v, num=2):
        level = state.levels
        cur_level = level[0].get_blocks()[v]
        for i in range(num):
            cur_level = level[0].get_blocks()[cur_level]
        return cur_level

    def block_analysis(self):
        blocks, state = self.original_block_model()
        tmp_table = pd.DataFrame(self.node_table)
        tmp_table['block'] = pd.Series(blocks)
        for i in range(tmp_table['block'].values.max()):
            li = list(tmp_table[tmp_table['block']==i].index)
            attr = []
            for node in li:
                for ele in self.get_node_feat(node):
                    attr.append(ele)
            ctr = Counter(attr)
            print i, len(li), [(self.feat_table.values[i[0]], i[1]) for i in ctr.most_common(5)]

    def prob_conn_by_feat(self, name, exact_match=False):
        """
        if the exact match mode is on, then name is the index number of the feature in the table
        :param name: string/int
        :param exact_match: bool
        :return: float, int
        """
        if exact_match:
            feat_indices = [int(name)]
        else:
            feat_indices = self.select_feat_by_name(name)
        sel_nodes = set()
        for feat in feat_indices:
            feat_index = self.attr_index_g2t(feat, False)
            neighbours = self.attr_network.vertex(feat_index).all_neighbours()
            sel_nodes |= set([self.attr_network.vertex_index[v] for v in neighbours])
        # print sel_nodes, len(sel_nodes)
        tmp_network = gt.Graph(self.network)
        tmp_network.vertex_properties['selected'] = tmp_network.new_vertex_property("bool")
        for index in sel_nodes:
            tmp_network.vertex_properties['selected'][index] = True
        tmp_network.set_vertex_filter(tmp_network.vertex_properties['selected'])
        # print gt.global_clustering(tmp_network), gt.global_clustering(self.network)
        # logging.debug('The network density of sub-graph: %f' % self.get_density(tmp_network))
        # logging.debug('The network density of original graph: %f' % self.get_density(self.network))
        return self.get_density(tmp_network, self.network.is_directed()), len(sel_nodes)

    def get_feat_density_table(self):
        den_list = []
        for i in range(self.feat_table.shape[0]):
            den, num = self.prob_conn_by_feat(i, True)
            den_list.append({'id': i, 'name': self.feat_table[FEAT_ID][i],'density': den, 'count': num})
        return pd.DataFrame(den_list)

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
