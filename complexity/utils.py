#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
"""
    Complexity: utils.py
    ~~~~~~~~~~~~~~~~~~~~

    General utils.

    :copyright: (c) 2015 Luke Southam <luke@devthe.com>.
    :license: New BSD, see LICENSE for more details.
"""

from flask import g
from custom import shelve


def get_shelve(flag="c"):
    """
    Gets shelves and caches them per request.
    """
    if hasattr(g, 'shelve'):
        f, s = g.shelve
        if flag == f:
            return s
        s.close()

    s = shelve.get_shelve(flag)
    g.shelve = (flag, s)

    return s

