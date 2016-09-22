# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

"""

SNAPdata
    -- database.py
    init_database

"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from rAnProject import ranfig as rfg

SUPPORTED_DATA_SET = {'GooglePlus': 'snap_gp',
                      'Facebook': 'snap_fb'}
Base = declarative_base()


def init_database_from_ranfig(ranfig_dir, data_set):
    ranfig = rfg.load_ranfig(ranfig_dir)
    database = ranfig['Database']
    engine = create_engine('%s://%s:%s@%s:%s/%s' %
                           (database['engine'], database['user'], database['password'],
                            database['host'], database['port'], SUPPORTED_DATA_SET[data_set]))
    return engine
