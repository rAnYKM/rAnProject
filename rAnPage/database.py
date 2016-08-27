# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

""" database.py - database module for demo

Based on sqlalchemy

"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import ranfig as rfg

ranfig = rfg.load_ranfig('settings.ini')
database = ranfig['Database']
engine = create_engine('%s://%s:%s@%s:%s/%s' %
                       (database['engine'], database['user'], database['password'],
                        database['host'], database['port'], database['db']))
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import any thing related
    import default_db.module_facebook
    Base.metadata.create_all(bind=engine)
