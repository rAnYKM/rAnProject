# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

"""

SNAPdata.Facebook
    -- fb_merge.py

Merge all the ego networks into a large one.

"""
import os
import logging
import networkx as nx
import pandas as pd
from fb_loader import FacebookEgoNet
from rAnProject.ranfig import load_ranfig
from rAnProject import settings


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
FACEBOOK_COMBINED = 'facebook_combined.txt'
EGO_LIST = ['0', '107', '348', '414', '686', '698', '1684', '1912', '3437', '3980']
DEFAULT_OUTPUT = 'facebook_complete'


def get_ego_node_feat(ego):
    fb = FacebookEgoNet(ego, build_network=False)
    # Here we only extract the feat table
    node_feat = fb.node_feats()
    # print node_feat
    feat_table = fb.feat_table
    return node_feat, feat_table


def initialize(ranfig_dir=settings.SETTINGS_DIR, filename=FACEBOOK_COMBINED, output=DEFAULT_OUTPUT):
    """
    Initialize the network with
    :return:
    """
    fb_dir = load_ranfig(ranfig_dir)['SNAP']['facebook']
    with open(os.path.join(fb_dir, filename), 'rb') as fp:
        lines = fp.readlines()
        edges = [line.strip('\r\n').split(' ') for line in lines]

    g = nx.Graph(directed=False)
    g.add_edges_from(edges)
    logging.debug('[fb_merge] %d nodes and %d edges loaded' % (g.number_of_nodes(), g.number_of_edges()))
    all_nodes = {}
    all_feats = pd.DataFrame()
    for ego in EGO_LIST:
        node_feat, feat_table = get_ego_node_feat(ego)
        all_nodes.update(node_feat)
        all_feats = all_feats.append(feat_table, ignore_index=True).drop_duplicates().reset_index(drop=True)
    aux_dict = {}
    new_node_list = []
    for ind, row in all_feats.iterrows():
        aux_dict[row['attr']] = ind
    for node, feat in all_nodes.iteritems():
        str_profile_index = ' '.join([str(aux_dict[fe]) for fe in feat])
        new_node_list.append({'user_id': node, 'profile': str_profile_index})
    node_df = pd.DataFrame(new_node_list)
    node_df.to_csv(DEFAULT_OUTPUT + '.nodes')
    all_feats.to_csv(DEFAULT_OUTPUT + '.feats')
    nx.write_graphml(g, DEFAULT_OUTPUT + '.graphml')


if __name__ == '__main__':
    initialize()
