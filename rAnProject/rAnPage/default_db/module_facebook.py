# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

""" snapdb.py - SNAP data set to MySQL data base

SNAP Google+ & Facebook Data Set

"""

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import rAnProject.settings as settings

from rAnProject import ranfig as rfg

Base = declarative_base()

class Nodes(Base):
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), index=True, nullable=False)

    def __repr__(self):
        return self.id, self.user_id


class Attributes(Base):
    __tablename__ = 'attributes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    attr_id = Column(String(255), index=True, nullable=False)
    category_1 = Column(String(255))
    category_2 = Column(String(255))
    category_3 = Column(String(255))


class Relations(Base):
    __tablename__ = 'relations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(255), ForeignKey('nodes.user_id'), nullable=False)
    destination = Column(String(255), ForeignKey('nodes.user_id'), nullable=False)


class AttributeLinks(Base):
    __tablename__ = 'attribute_links'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(255), ForeignKey('nodes.user_id'), nullable=False)
    attr = Column(String(255), ForeignKey('attributes.attr_id'), nullable=False)

def initialize():
    ranfig = rfg.load_ranfig(settings.SETTINGS_DIR)
    database = ranfig['Database']
    engine = create_engine('%s://%s:%s@%s:%s/%s' %
                           (database['engine'], database['user'], database['password'],
                            database['host'], database['port'], database['db']))
    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
