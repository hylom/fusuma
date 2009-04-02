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


_story_template = """<div class="article">
<h3><a name="${fn}">${title}</a></h3>
${body}
<div class="footer">
<span class="posted">[posted at ${ti}]</span>
path: <a href="${base_url}/${absolute_path_urlencoded}" title="path">/${absolute_path}</a>
<a href="${base_url}/${file_path_urlencoded}.${flavour}">permlink</a>
</div>
</div>
"""

_new_story_template = """[%insert(http_header)%]
[%insert(html_header)%]

${preview_html}

<div id="story-edit">
<form action="${SCRIPT_NAME}/new_story/" method="post">
  <div>
    <label for="story-edit-filename">filename:</label>
    <input type="text" name="filename" id="story-edit-filename">
  </div>
  <div>
    <label for="story-edit-title">title:</label>
    <input type="text" name="title" id="story-edit-title">
  </div>
  <div>
    <label for="story-edit-date">date:</label>
    <input type="text" name="date" id="story-edit-date">
  </div>
  <div>
    <label for="">body:</label>
    <textarea name="body" id="story-edit-body"></textarea>
  </div>
  <div>
    <label for="story-edit-tags">tags:</label>
    <input type="text" name="tags" id="story-edit-tags">
  </div>
  <div>
    <input name="mode" type="submit" value="preview">
    <input name="mode" type="submit" value="post">
  </div>
</div>

[%insert(html_footer)%]
"""

def fsm_add_handlers(fsm):
    regex = re.compile(r"^/new_story/")
    fsm.append_url_handler( regex, new_story )
    fsm.add_template("story.html", _story_template)
    fsm.add_template("new_story", _new_story_template)

def new_story(fsm):
    """
    Handler for http://server.name/<cgi_pathname>/new_story/
    """

#        print self.http_header("text/html; charset=utf-8;")

    mode = fsm.param("mode")
    args = dict( title = "new story",
                 preview_html = "" )

    if mode == "preview":
        prv_args = dict()
        prv_args["title"] = fsm.param("title")
        prv_args["date"] = fsm.param("date")
        prv_args["body"] = fsm.param("body")
        prv_args["tags"] = fsm.param("tags")
        prv_args["mode"] = fsm.param("mode")
        preview = fsm.parse_template( "story.html", prv_args )
        args["preview_html"] = preview
    elif mode == "post":
        pass

    print fsm.parse_template( "new_story", args )

def _stringfy(strings):
    """
    build text-data from title, body, ...
    """

def _post(fsm, string, date):
    """
    do post operation.
    """
    
