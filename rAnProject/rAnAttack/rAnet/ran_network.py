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

import graph_tool.all as gt
from rAnProject.SNAPdata.GooglePlus.gp_network import GPEgoNetwork


class Ranet:
    """
    Ranet includes at least the following 4 parts:
    1. node_table
    2. edge_table/relation_table
    3. feat_table/attribute_table
    4. link_table/attribute_link_table
    which is similar with RanGraph

    """
    def load_network_from_snap_gp(self, ego):
        gp_ego = GPEgoNetwork(ego)


    def __init__(self, is_directed=True):
        self.is_directed = is_directed
        self.network = gt.Graph(directed=is_directed)