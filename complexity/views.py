#!/usr/bin/assets python2
# -*- coding: UTF-8 -*-
"""
    Complexity: Flask views.
    ~~~~~~~~~~~~~~~~~~~~~~~~
    
    Contains the views and registers blueprints.

    :copyright: (c) 2014 Luke Southam <luke@devthe.com>.
    :license: New BSD, see LICENSE for more details.
"""

from . import app
from quiz import quiz_bp

from flask import render_template
from utils import get_shelve

@app.route("/")
def index():
    """
    The index page.
    Just welcomes the user and asks them to start a quiz. 
    """
    return render_template('index.html')


# TODO: Remove for release.
@app.route("/shelve")
def show_shelve():
    return str(dict(get_shelve()))


# Register blueprints.
app.register_blueprint(quiz_bp, url_prefix="/quiz")
