#!/usr/bin/env python
#######################################################################
# This file is part of Fusuma website management system.
#
# Copyright (c) hylom <hylomm at gmail.com>, 2008.
# 
# This file is released under the GPL.
#
# $Id: Fusuma.py,v 1.6 2009/01/04 18:27:48 hylom Exp $
#######################################################################
"""
This is Fusuma's RSS import plugin.
"""

__revision__ = "$Revision: 1.0 $"

import cgi
import sys
import os
from stat import *
import Cookie
import datetime
import time
import locale
import dircache
import re

import TCGITools
import PasswordMan
import BackWall
from SessionMan import SessionMan
from TemplateMan import TemplateMan

VERSION = "0.0.1"
VERSION_DATE = VERSION + " 01/18/2009"
VERSION_SPLIT = tuple(VERSION.split('.'))

def fsm_add_handlers(fsm):
    regex = re.compile(r"^/new_story/")
    fsm.append_url_handler( regex, new_story )

def new_story(fsm):
    """
    Handler for http://server.name/<cgi_pathname>/new_story/
    """

#        print self.http_header("text/html; charset=utf-8;")

    mode = fsm.param("mode")
    args = dict( title = "new story",
                 preview_html = "" )

    if mode == "preview" :
        prv_args = dict()
        prv_args["title"] = fsm.param("title")
        prv_args["date"] = fsm.param("date")
        prv_args["body"] = fsm.param("body")
        prv_args["tags"] = fsm.param("tags")
        prv_args["mode"] = fsm.param("mode")
        preview = fsm.parse_template( "story.html", prv_args )
        args["preview_html"] = preview

    print fsm.parse_template( "new_story", args )
