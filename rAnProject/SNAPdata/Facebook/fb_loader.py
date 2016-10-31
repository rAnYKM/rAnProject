# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

"""

SNAPdata.Facebook
    -- fb_loader.py

"""
import logging
import os
import time
import pandas as pd
import graph_tool.all as gt

from rAnProject import ranfig as rfg
import rAnProject.settings as settings
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


COLUMNS = {
    'edges': ['start', 'end', 'root'],
    'nodes': ['user_id', 'profile', 'root'],
    'attributes': ['attr', 'category', 'root'],
    'links': ['user_id', 'attr', 'root']
}


def get_ego_nodes(ego_node_dir=settings.FACEBOOK_EGO_NODE_LIST_DIR):
    with open(ego_node_dir, 'rb') as fp:
        nodes = [node.strip() for node in fp.readlines()]
    return nodes


class FacebookEgoNet:
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
        with open(os.path.join(self.dirs['facebook'], self.ego + '.featnames'), 'rb') as fp:
            feat_name = [self.__feat_process(line) for line in fp.readlines()]
            logging.debug('%d Feat(s) have been loaded.' % len(feat_name))
            return feat_name

    def __node_feat_list(self):
        with open(os.path.join(self.dirs['facebook'], self.ego + '.feat'), 'rb') as fp:
            nodes = [self.__node_process(feat) for feat in fp.readlines()]
            logging.debug('%d User Feature List(s) have been loaded.' % len(nodes))
            return nodes

    def __ego_feat_list(self):
        with open(os.path.join(self.dirs['facebook'], self.ego + '.egofeat'), 'rb') as fp:
            li = fp.readline().strip('\r\n').split(' ')
            index = [num for num, value in enumerate(li) if value == '1']
            logging.debug('%d Ego Feature(s) have been loaded.' % len(index))
            return index

    def __edge_list(self):
        with open(os.path.join(self.dirs['facebook'], self.ego + '.edges'), 'rb') as fp:
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

    def gen_tables(self):
        node_dict = self.__node_feat_list()
        feats = self.__feat_name_list()
        edges, _ = self.__edge_list()
        pre_node = []
        pre_edge = []
        pre_attr = []
        pre_link = []
        for node, profile in node_dict:
            tmp_node = {'user_id': node, 'profile': ' '.join([str(p) for p in profile])}
            pre_node.append(tmp_node)
            for p in profile:
                tmp_link = {'user_id': node, 'attr': p}
                pre_link.append(tmp_link)
        for feat, cate in feats:
            tmp_attr = {'attr': 'a' + self.__abbr_attr(cate) + feat, 'category': '|'.join(cate)}
            pre_attr.append(tmp_attr)
        for edge in edges:
            tmp_edge = {'start': edge[0], 'end': edge[1]}
            pre_edge.append(tmp_edge)
        return pd.DataFrame(pre_node), pd.DataFrame(pre_edge), pd.DataFrame(pre_attr), pd.DataFrame(pre_link)

    def __build_ego_network(self):
        t0 = time.time()
        network = gt.Graph(directed=False)
        network.add_vertex(len(self.aux_node_dict.keys()))
        # e_list = [(row[COLUMNS['edges'][0]], row[COLUMNS['edges'][1]])
        #           for index, row in self.relation_table.iterrows()]
        edges = [(self.aux_node_dict[row[COLUMNS['edges'][0]]],
                  self.aux_node_dict[row[COLUMNS['edges'][1]]])
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
        edge_list = [(self.aux_node_dict[row[COLUMNS['links'][0]]],
                      row[COLUMNS['links'][1]] + len(self.aux_node_dict.keys()))
                     for index, row in self.link_table.iterrows()]
        network.add_edge_list(edge_list)
        logging.debug('[Graph-tool] build attribute network in %fs' % (time.time() - t0))
        # state = gt.minimize_nested_blockmodel_dl(network, deg_corr=True)
        return network

    def get_aux_dict(self):
        """
        Get the auxiliary node and feature dictionary
        uid -> index
        category: feature -> index
        :return: dict, dict
        """
        nodes = self.node_table['user_id']
        feats = [value[1] + ':' + str(value[0])
                 for value in self.feat_table.values]
        return {node: index for index, node in nodes.iteritems()}, {feat: index for index, feat in enumerate(feats)}

    def __init__(self, ego, ranfig_dir=settings.SETTINGS_DIR):
        self.ranfig = ranfig_dir
        self.egos = get_ego_nodes()
        if ego not in self.egos:
            raise ValueError('Ego Network #%s does not exist.' % ego)
        self.ego = ego
        self.dirs = rfg.load_ranfig(self.ranfig)['SNAP']
        t0 = time.time()
        self.node_table, self.relation_table, self.feat_table, self.link_table = self.gen_tables()
        # print self.link_table
        # print self.node_table, self.relation_table, self.feat_table, self.link_table
        self.aux_node_dict, self.aux_feat_dict = self.get_aux_dict()
        # print self.aux_node_dict, self.aux_feat_dict
        self.network = self.__build_ego_network()
        self.attr_network = self.__build_attr_network()
        logging.debug('Ego Network #%s Loaded in %f s' % (self.ego, time.time() - t0))
