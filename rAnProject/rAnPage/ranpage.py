# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

""" demo.py - a simple user interface for demonstration

Based on Flask micro-architecture

"""

from flask import Flask, request, redirect, url_for, render_template
from rAnProject.rAnPage.database import db_session
from rAnProject.rAnPage.default_db.module_facebook import *
from sqlalchemy import func, or_
from rAnProject.rAnPriv.ran_graph import RanGraph

app = Flask(__name__)

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='ran',
    PASSWORD='root'
))


def get_ran():
    soc_q = db_session.query(Nodes.user_id)
    att_q = db_session.query(Attributes.attr_id)
    edg_q = db_session.query(Relations.source, Relations.destination)
    lin_q = db_session.query(AttributeLinks.user, AttributeLinks.attr)
    soc = [row[0] for row in soc_q]
    att = [row[0] for row in att_q]
    edg = [(row[0], row[1]) for row in edg_q]
    lin = [(row[0], row[1]) for row in lin_q]
    ran = RanGraph(soc, att, edg, lin)
    return ran


@app.route('/', methods=['GET'])
def show_entries():
    page = request.args.get('p', '1')
    if not page:
        page = 1
    limit = request.args.get('limit', '20')
    if not limit:
        limit = 20
    total = db_session.query(func.count(Nodes.id)).one()[0]
    res = db_session.query(Nodes.id, Nodes.user_id).order_by(Nodes.id). \
        limit(int(limit)).offset((int(page) - 1) * int(limit))
    entries = [dict(sid=row[0], uid=row[1]) for row in res]
    pager = {'total': int(total), 'limit': int(limit), 'curr_page': int(page)}
    return render_template('show_entries.html', entries=entries, p=pager)


@app.route('/user/<uid>/', methods=['GET'])
def show_profile(uid):
    page = request.args.get('p', '1')
    if not page:
        page = 1
    limit = request.args.get('limit', '10')
    if not limit:
        limit = 10
    if not uid:
        uid = 0
    res = db_session.query(AttributeLinks.attr).filter(AttributeLinks.user == uid)
    profile = list()
    for row in res:
        sub_res = db_session.query(Attributes.category_1, Attributes.category_2, Attributes.category_3). \
            filter(Attributes.attr_id == row[0])[0]
        profile.append(dict(att=row[0], c1=sub_res[0], c2=sub_res[1], c3=sub_res[2]))
    res2 = db_session.query(Relations.source, Relations.destination). \
        filter(or_(Relations.source == uid, Relations.destination == uid)). \
        limit(int(limit)).offset((int(page) - 1) * int(limit))
    total = db_session.query(func.count(Relations.id)). \
        filter(or_(Relations.source == uid, Relations.destination == uid)).one()[0]
    friend = set()
    for row in res2:
        if row[0] == uid:
            friend.add(row[1])
        else:
            friend.add(row[0])
    pager = {'total': int(total), 'limit': int(limit), 'curr_page': int(page)}
    return render_template('show_profile.html', profile=profile, friend=list(friend), user=uid, p=pager)


@app.route('/ranpriv/result/<uid>/', methods=['GET'])
def protection(uid):
    ran = get_ran()
    secrets = request.args.getlist('secrets')
    level = int(request.args.get('level', '0'))
    price = {att: 1 for att in ran.attr_node}
    price_r = {n: 1 for n in ran.soc_node}
    strict = [len(ran.soc_attr_net.neighbors(secret)) / float(ran.soc_net.number_of_nodes()) for secret in secrets]
    epsilon = [min(st + 0.1 + level * 0.2, 0.8) for st in strict]
    attr = ran.single_protection(uid, secrets, price, epsilon, 'greedy', 'single')
    soc = ran.single_s_relation(uid, secrets, price_r, epsilon, 'greedy')
    profile = list()
    friend = [node[1] for node in soc]
    for row in attr:
        sub_res = db_session.query(Attributes.category_1, Attributes.category_2, Attributes.category_3). \
            filter(Attributes.attr_id == row)[0]
        profile.append(dict(att=row, c1=sub_res[0], c2=sub_res[1], c3=sub_res[2]))
    return render_template('show_results.html', profile=profile, friend=friend, user=uid)


@app.route('/ranpriv/settings/<uid>/', methods=['GET', 'POST'])
def settings(uid):
    res = db_session.query(AttributeLinks.attr).filter(AttributeLinks.user == uid)
    profile = list()
    attr = list()
    for row in res:
        sub_res = db_session.query(Attributes.category_1, Attributes.category_2, Attributes.category_3). \
            filter(Attributes.attr_id == row[0])[0]
        profile.append(dict(att=row[0], c1=sub_res[0], c2=sub_res[1], c3=sub_res[2]))
        attr.append(row[0])
    if request.method == 'POST':
        secret = [att for att in request.form.getlist('choose')]
        level = request.form['level']
        if not level:
            level = 0
        else:
            level = int(level)
        return redirect(url_for('protection', uid=uid, secrets=secret, level=level))
    return render_template('settings.html', profile=profile, user=uid)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
    app.run()
