# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

"""

rAnAttack.rAnet
    -- ran_featset.py

"""

class RanFeatSet:
    def __renew_feat_set(self):
        self.current_set = self.u_set
        for name, neighbor in self.feat_pool:
            self.current_set &= neighbor

    def add_feat(self, name, neighbor):
        self.feat_pool.append((name, neighbor))
        self.current_set &= neighbor

    def common_neighbor(self, neighbor):
        return self.current_set & neighbor

    def remove_feat_index(self, index):
        self.feat_pool.pop(index)
        self.__renew_feat_set()

    def __init__(self, universal_node_set):
        self.u_set = universal_node_set
        self.current_set = self.u_set
        self.feat_pool = list()
