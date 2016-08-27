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

app = Flask(__name__)

app.config.update(dict(
    DEBUG=False,
    SECRET_KEY='development key',
    USERNAME='ran',
    PASSWORD='root'
))

@app.route('/')
def show_entries():
    res = db_session.query(Nodes.id, Nodes.user_id)
    entries = [dict(sid=row[0], uid=row[1]) for row in res]
    return render_template('show_entries.html', entries=entries)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run()
