#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
"""
    Complexity: quiz.py
    ~~~~~~~~~~~~~~~~~~~
    
    Contains the quiz blueprint.

    Copyright: (c) 2014 Luke Southam <luke@devthe.com>.
    License: New BSD, see LICENSE for more details.
"""
from functools import wraps

from flask import (Blueprint, render_template, request, redirect,
                   url_for, abort, g, make_response)
from flask.ext import shelve

from cookies import Cookie
from utils import get_shelve
from quizes import quizes, quizes_rev, quizes_path, load_quiz, BaseQuiz

from . import app

COOKIE_QUIZ = 'quiz'

quiz = Blueprint('quiz', __name__, template_folder='templates/quizes')

def quiz_cookie_manage(response):
    """
    Manages quiz instances set at g.quiz_id

    Used by controllers with @after_request.
    """
    quiz_req = Cookie(request.cookies.get(COOKIE_QUIZ), False).data

    quiz_resp = None
    if hasattr(g, 'quiz_id'):
        quiz_resp = g.quiz_id
    
    # No more instances.
    if quiz_resp is None:
        if quiz_req is None:
            # There wasn't any instances. Still aren't.
            return
        
        # The instance did not get renewed.
        try:
            BaseQuiz.remove_instance(get_shelve('c'), quiz_req)
        except KeyError:
            pass
        return response.set_cookie(COOKIE_QUIZ, '', expires=0)
    
    # Still an instance, but not the same as before (may not have
    # been one before).
    if quiz_resp != quiz_req:
        if quiz_req is not None:
            # Old instance has been replaced.
            try:
                BaseQuiz.remove_instance(get_shelve('c'), quiz_req)
            except KeyError:
                pass

        # A new instance has been created.
        return response.set_cookie(COOKIE_QUIZ, Cookie(quiz_resp).value)
    
    # If no return by now, nothing has changed.

def quiz_cookie(func):
    """
    Runs quiz_cookie_manage on response object after request.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if isinstance(response, unicode):
            response = make_response(response)

        quiz_cookie_manage(response)
        return response
    return wrapper

@quiz.route("/")
@quiz_cookie
def choose():
    """
    Get user to choose which quiz.

    Returns a HTML page with a form, then redircts them to the
    correct quiz's page once the form is submited.
    """

    # Ask user which quiz.
    if 'quiz' not in request.args:
        return render_template('new.html', quizes=quizes)

    # Redirect quiz request to the correct page.
    return redirect(
        url_for(
            'quiz.attempt',
            quiz_module=request.args['quiz']
        )
    )

@quiz.route("/<quiz_module>")
@quiz_cookie
def attempt(quiz_module):
    """
    Attempt the quiz.

    Returns the HTML page for the quiz.

    Args:
        quiz_module (str): The name of the module in the `quizes`
                           package where the `Quiz` class exists.

    Raises:
        abort(404): When the requested `quiz_module` does not exist.
    """

    # Check that the quiz exists.
    if quiz_module not in quizes.values():
        raise abort(404)

    template_vars = {}
    
    template_vars['quiz_name'] = quizes_rev[quiz_module]
    template_vars['quiz_module'] = quiz_module
    template_vars['SCRIPT_QUIZ_URLS'] = {
        rule.endpoint[len('quiz._'):]:
            url_for(rule.endpoint, quiz_module=quiz_module)
                for rule in app.url_map.iter_rules()
                    if rule.endpoint.startswith('quiz._')     
    }

    return render_template("%s.html" % quiz_module, **template_vars)

# NOTE: Endpoints accessed by client side scripts begin with a '_'

@quiz.route("/<quiz_module>/_new")
@quiz_cookie
def _new(quiz_module):
    """
    Create a new quiz instance.

    Used by client side code to get a quiz instance.

    Args:
        quiz_module (str): The name of the module in the `quizes`
                           package where the `Quiz` class exists.

    Returns:
        str: The Quiz instance's ID.

    Raises:
        abort(404): When the requested `quiz_module` does not exist.
    """

    # Check the quiz exists.
    if quiz_module not in quizes.values():
        raise abort(404)
    
    Quiz = load_quiz(quiz_module) 
    
    g.quiz_id = Quiz.create_new(get_shelve())
    
    return make_response(g.quiz_id)

@quiz.route("/<quiz_module>/_next", methods=['GET', 'POST'])
@quiz_cookie
def _next(quiz_module):
    quiz_id = Cookie(request.cookies.get(COOKIE_QUIZ), False).data
    if quiz_id == None:
        abort(400)

    quiz = load_quiz(quiz_module).get_instance(get_shelve(), quiz_id)

    return quiz.next()

