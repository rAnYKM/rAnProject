# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

"""

SNAPdata.GooglePlus
    -- build_raw_database.py

"""
import csv
import logging
import os
import time

from SNAPdata.GooglePlus.tables import *

from rAnProject import ranfig as rfg

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
    line = line.strip().split(':')
    return [line[1], line[0].split(' ')[1]]


def load_feats(uid, dirs):
    with open(os.path.join(dirs, uid + '.featnames'), 'rb') as fp:
        feats = [__process_raw_feat_line(line) for line in fp.readlines()]
    return feats


def __process_core_edge(edge, uid, flag=True):
    col = COLUMNS['edges']
    tmp = {col[0]: edge[0], col[1]: edge[1]}
    if flag:
        tmp[col[2]] = uid
    return tmp


def __process_core_node(node, uid, flag=True):
    col = COLUMNS['nodes']
    tmp = {col[0]: node[0], col[1]: node[1]}
    if flag:
        tmp[col[2]] = uid
    return tmp


def __process_core_feat(attr, uid, flag=True):
    col = COLUMNS['attributes']
    tmp = {col[0]: attr[0], col[1]: attr[1]}
    if flag:
        tmp[col[2]] = uid
    return tmp


def make_block(li, size=BLOCK_SIZE):
    blocks = []
    index = 0
    while len(li[index:]) >= size:
        blocks.append(li[index: index + size])
        index += size
    blocks.append(li[index:])
    logging.debug('Divided into %d blocks with size=%d' % (len(blocks), size))
    return blocks


def csv_builder(ranfig_dir):
    rfg_settings = rfg.load_ranfig(ranfig_dir)
    dirs = rfg_settings['SNAP']['googleplus']
    ego_nodes = get_ego_nodes()
    logging.debug('Begin to build the database')
    if not os.path.exists(os.path.join(dirs, 'csv')):
        os.makedirs(os.path.join(dirs, 'csv'))
    for index, ego in enumerate(ego_nodes):
        starts = time.time()
        edges = load_edges(ego, dirs)
        nodes = load_nodes(ego, dirs)
        feats = load_feats(ego, dirs)
        # edge_checker(edges, nodes)
        logging.debug('size: %d, %d, %d' % (len(nodes), len(edges), len(feats)))
        if len(edges) == 0 or len(feats) == 0:
            logging.debug('No.%d ego network #%s has neither edges nor features, skipped' % (index, ego))
            continue
        core_edges = [__process_core_edge(edge, ego, False) for edge in edges]
        core_nodes = [__process_core_node(node, ego, False) for node in nodes]
        core_feats = [__process_core_feat(attr, ego, False) for attr in feats]
        with open(os.path.join(dirs, 'csv', ego + '-node.csv'), 'wb') as fp:
            writer = csv.DictWriter(fp, fieldnames=COLUMNS['nodes'][:-1])
            writer.writeheader()
            writer.writerows(core_nodes)
        with open(os.path.join(dirs, 'csv', ego + '-edge.csv'), 'wb') as fp:
            writer = csv.DictWriter(fp, fieldnames=COLUMNS['edges'][:-1])
            writer.writeheader()
            writer.writerows(core_edges)
        with open(os.path.join(dirs, 'csv', ego + '-feat.csv'), 'wb') as fp:
            writer = csv.DictWriter(fp, fieldnames=COLUMNS['attributes'][:-1])
            writer.writeheader()
            writer.writerows(core_feats)
        logging.debug('Finish adding No.%d ego network #%s in %f s' % (index, ego, time.time() - starts))


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
        if len(edges) == 0 or len(feats) == 0:
            logging.debug('No.%d ego network #%s has neither edges nor features, skipped' % (index, ego))
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
    csv_builder('../../settings.ini')
