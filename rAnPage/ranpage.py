# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

""" demo.py - a simple user interface for demonstration

Based on Flask micro-architecture

"""

import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from rAnPage.database import db_session
from rAnPage.default_db.module_facebook import *
from sqlalchemy import func, or_

app = Flask(__name__)

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='ran',
    PASSWORD='root'
))


@app.route('/', methods=['GET'])
def show_entries():
    page = request.args.get('p', '1')
    if not page:
        page = 1
    limit = request.args.get('limit', '20')
    if not limit:
        limit = 20
    total = db_session.query(func.count(Nodes.id)).one()[0]
    res = db_session.query(Nodes.id, Nodes.user_id).order_by(Nodes.id).\
            limit(int(limit)).offset((int(page) - 1) * int(limit))
    entries = [dict(sid=row[0], uid=row[1]) for row in res]
    pager = {'total': int(total), 'limit': int(limit), 'curr_page': int(page)}
    return render_template('show_entries.html', entries=entries, p=pager)


@app.route('/user/<uid>/', methods=['GET'])
def show_profile(uid):
    page = request.args.get('p', '1')
    if not page:
        page = 1
    limit = request.args.get('limit', '20')
    if not limit:
        limit = 20
    if not uid:
        uid = 0
    res = db_session.query(AttributeLinks.attr).filter(AttributeLinks.user==uid)
    profile = list()
    for row in res:
        sub_res = db_session.query(Attributes.category_1, Attributes.category_2, Attributes.category_3).\
            filter(Attributes.attr_id==row[0])[0]
        profile.append(dict(att=row[0], c1=sub_res[0], c2=sub_res[1], c3=sub_res[2]))
    res2 = db_session.query(Relations.source, Relations.destination).\
        filter(or_(Relations.source == uid, Relations.destination == uid)). \
        limit(int(limit)).offset((int(page) - 1) * int(limit))
    total = db_session.query(func.count(Relations.id)).\
        filter(or_(Relations.source == uid, Relations.destination == uid)).one()[0]
    friend = list()
    for row in res2:
        if row[0] == uid:
            friend.append(row[1])
        else:
            friend.append(row[0])
    pager = {'total': int(total), 'limit': int(limit), 'curr_page': int(page)}
    return render_template('show_profile.html', profile=profile, friend=friend, user=uid, p=pager)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
    app.run()
