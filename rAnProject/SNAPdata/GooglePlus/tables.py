# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

"""

SNAPdata.GooglePlus
    -- tables.py
    sqlalchemy declarative

"""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from SNAPdata.database import init_database_from_ranfig
Base = declarative_base()

COLUMNS = {
    'edges': ['start', 'end', 'root'],
    'nodes': ['user_id', 'profile', 'root'],
    'attributes': ['attr', 'category', 'root'],
    'links': ['user_id', 'attr', 'root']
}
RANFIG_DIR = '../../settings.ini'


class Edges(Base):
    __tablename__ = 'edges'
    id = Column(Integer, primary_key=True, autoincrement=True)
    start = Column(String(255), nullable=False)
    end = Column(String(255), nullable=False)
    root = Column(String(255), index=True, nullable=False)


class Nodes(Base):
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), index=True, nullable=False)
    profile = Column(Text, nullable=False)
    root = Column(String(255), index=True, nullable=False)


class Attributes(Base):
    __tablename__ = 'attributes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    attr = Column(String(255), index=True, nullable=True)
    category = Column(String(255))
    root = Column(String(255), index=True, nullable=False)


def initialize():
    engine = init_database_from_ranfig(RANFIG_DIR, 'GooglePlus')
    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
