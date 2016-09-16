# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

"""

SNAPdata.GooglePlus
    -- build_raw_database.py

"""
import os
import time
import logging
from SNAPdata.GooglePlus.tables import *
import ranfig as rfg

DEFAULT_EGO_NODE_LIST = 'nodeList.txt'
Base = declarative_base()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
BLOCK_SIZE = 10000


def get_ego_nodes(ego_node_dir=DEFAULT_EGO_NODE_LIST):
    with open(ego_node_dir, 'rb') as fp:
        nodes = [node.strip() for node in fp.readlines()]
    return nodes


def edge_checker(edges, nodes):
    uid = [n[0] for n in nodes]
    num = 0
    for i in edges:
        if i[0] not in uid:
            num += 1
        if i[1] not in uid:
            num += 1
    if num > 0:
        logging.error('%d edge nodes not in the node table' % num)


def load_edges(uid, dirs):
    with open(os.path.join(dirs, uid + '.edges'), 'rb') as fp:
        edges = [edge.strip().split(' ') for edge in fp.readlines()]
    # with open(os.path.join(dir, uid + '.followers'), 'rb') as fp:
    #    edges += [[edge.strip(), uid] for edge in fp.readlines()]
    return edges


def __process_raw_node_line(line):
    line = line.strip().split(' ')
    uid = line[0]
    profile = ' '.join(line[1:])
    return [uid, profile]


def load_nodes(uid, dirs):
    with open(os.path.join(dirs, uid + '.egofeat'), 'rb') as fp:
        nodes = [[uid, fp.readline().strip()]]
    with open(os.path.join(dirs, uid + '.feat'), 'rb') as fp:
        nodes += [__process_raw_node_line(line) for line in fp.readlines()]
    return nodes


def __process_raw_feat_line(line):
    line = line.strip().split(' ')[1].split(':')
    return [line[1], line[0]]


def load_feats(uid, dirs):
    with open(os.path.join(dirs, uid + '.featnames'), 'rb') as fp:
        feats = [__process_raw_feat_line(line) for line in fp.readlines()]
    return feats


def __process_core_edge(edge, uid):
    col = COLUMNS['edges']
    return {col[0]: edge[0], col[1]: edge[1], col[2]: uid}


def __process_core_node(node, uid):
    col = COLUMNS['nodes']
    return {col[0]: node[0], col[1]: node[1], col[2]: uid}


def __process_core_feat(attr, uid):
    col = COLUMNS['attributes']
    return {col[0]: attr[0], col[1]: attr[1], col[2]: uid}


def make_block(li, size=BLOCK_SIZE):
    blocks = []
    index = 0
    while (len(li[index:]) >= size):
        blocks.append(li[index: index + size])
        index += size
    blocks.append(li[index:])
    logging.debug('Divided into %d blocks with size=%d' % (len(blocks), size))
    return blocks


def init_builder(ranfig_dir):
    rfg_settings = rfg.load_ranfig(ranfig_dir)
    dirs = rfg_settings['SNAP']['googleplus']
    ego_nodes = get_ego_nodes()
    logging.debug('Begin to build the database')
    for index, ego in enumerate(ego_nodes):
        starts = time.time()
        edges = load_edges(ego, dirs)
        nodes = load_nodes(ego, dirs)
        feats = load_feats(ego, dirs)
        # edge_checker(edges, nodes)
        logging.debug('size: %d, %d, %d' % (len(nodes), len(edges), len(feats)))
        if len(edges) == 0:
            logging.debug('No.%d ego network #%s no edges, skipped' % (index, ego))
            continue
        # sqlalchemy core format
        core_edges = [__process_core_edge(edge, ego) for edge in edges]
        core_nodes = [__process_core_node(node, ego) for node in nodes]
        core_feats = [__process_core_feat(attr, ego) for attr in feats]
        engines = init_database_from_ranfig(ranfig_dir, 'GooglePlus')
        for block in make_block(core_nodes, 500):
            engines.execute(
                Nodes.__table__.insert(),
                block
            )
        for block in make_block(core_edges):
            engines.execute(
                Edges.__table__.insert(),
                block
            )
        for block in make_block(core_feats):
            engines.execute(
                Attributes.__table__.insert(),
                block
            )
        logging.debug('Finish adding No.%d ego network #%s in %f s' % (index, ego, time.time() - starts))


if __name__ == '__main__':
    init_builder('../../settings.ini')
