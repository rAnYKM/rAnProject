# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

"""

rAnet
    -- kronecker_graph.py

"""

import numpy as np
import graph_tool.all as gt


def prob_empty_graph(theta, k):
    # log（1-x) approx -x-0.5*x**2
    le = -theta.sum()**k - 0.5*np.square(theta).sum()**k
    return le


def prob_graph(theta, sigma, graph, k):
    le = prob_empty_graph(theta, k)
    if graph is None:
        graph = gt.Graph()
    pk = np.kron(theta, k)
    l = le
    for edge in graph.edges():
        u = edge.source()
        v = edge.target()
        p_uv = pk.item((sigma[u], sigma[v]))
        l += -np.log2(1 - p_uv) + np.log2(p_uv)
    return l


def kronecker_fit(n1, n, rate, converge):
    # Initialize theta1
    l0 = 0
    l = 1
    while l - l0 < converge:
        # gradient
        # update parameter
        pass
    return
