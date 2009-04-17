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
import codecs

import TCGITools
import PasswordMan
import BackWall
from SessionMan import SessionMan
from TemplateMan import TemplateMan

VERSION = "0.0.1"
VERSION_DATE = VERSION + " 01/18/2009"
VERSION_SPLIT = tuple(VERSION.split('.'))


_story_template = """<div class="article">
<h3><a name="${fn}">${se_title}</a></h3>
${se_body}
<div class="footer">
<span class="posted">[posted at ${ti}]</span>
path: <a href="${base_url}/${absolute_path_urlencoded}" title="path">/${absolute_path}</a>
<a href="${base_url}/${file_path_urlencoded}.${flavour}">permlink</a>
</div>
</div>
"""

_new_story_template = """[%insert(http_header)%]
[%insert(html_header)%]
[%insert(general_header)%]

${preview_html}
<hr>
<div id="story-edit">
<form action="${SCRIPT_NAME}/new_story/" method="post">
  <div>
    <label for="story-edit-filename">filename:</label>
    <input type="text" name="se_filename" id="story-edit-filename"
           value="${se_filename}" size="80">.txt
  </div>
  <div>
    <label for="story-edit-title">title:</label>
    <input type="text" name="se_title" id="story-edit-title"
           value="${se_title}" size="80">
  </div>
  <div>
    <label for="story-edit-date">date:</label>
    <input type="text" name="se_date" id="story-edit-date"
           value="${se_date}" size="80">
  </div>
  <div>
    <label for="">body:</label>
    <textarea name="se_body" id="story-edit-body" cols="80" rows="20" wrap="soft">${se_body}</textarea>
  </div>
  <div>
    <label for="story-edit-tags">tags:</label>
    <input type="text" name="se_tags" id="story-edit-tags" value="${se_tags}" size="80">
  </div>
  ${select_form}
  <div>
    <input name="mode" type="submit" value="preview">
    <input name="mode" type="submit" value="post">
  </div>
</div>

[%insert(html_footer)%]
"""

_dir_select_template_begin = """<div><select name="se_dir" id="story-edit-dir">
"""

_dir_select_template_elems = """  <option value="%(val)s">%(key)s</option>
"""

_dir_select_template_end = """</select></div>
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

    select_form = _dir_select_template_begin
    # build select form
    for dir in _get_directories(fsm):
        select_form = select_form + _dir_select_template_elems % {"val":dir, "key":dir}
    select_form = select_form + _dir_select_template_end
        
    mode = fsm.param("mode")
    args = {"title":"new story",
            "preview_html":"",
            "select_form":select_form,
            "se_title":"",
            "se_date":"",
            "se_body":"",
            "se_tags":"",
            "se_mode":"",
            "se_filename":"",
            
            }

    if mode == "preview":
        prv_args = {}
        prv_args["se_title"] = fsm.param("se_title")
        prv_args["se_date"] = fsm.param("se_date")
        prv_args["se_body"] = fsm.param("se_body")
        prv_args["se_tags"] = fsm.param("se_tags")
        prv_args["se_mode"] = fsm.param("se_mode")
        prv_args["se_filename"] = fsm.param("se_filename")
        preview = fsm.parse_template( "story.html", prv_args )

        args.update(prv_args)
        args["preview_html"] = preview

    elif mode == "post":
        rpath = fsm.param("se_dir") + fsm.param("se_filename") + ".txt"
        output_path = fsm.get_py_cfg("datadir") + rpath
#        try:
        if os.path.exists(output_path):
            raise Exception("file_exists")
#        file = codecs.open(output_path, "w", "utf_8")
        file = open(output_path, "w")
#        except Exception, mesg:
#            pass
        print >> file, fsm.param("se_title")
        if len(fsm.param("se_tags")) > 0:
            print >> file, "#tag ", fsm.param("se_tags")
        print >> file, fsm.param("se_body")
        file.close()

        editor_url = fsm.script_name() + "/editor" + rpath + "?op=edit"
        print fsm.http_header()
        print fsm.html_redirection(editor_url)
        return

    print fsm.parse_template( "new_story", args )


def _get_directories(fsm):
    """
    get directries.
    """
    dir = fsm.get_py_cfg("datadir")
    list = dircache.listdir(dir)
    dirs = ["/"]
    for item in list:
        if os.path.isdir(os.path.join(dir, item)):
            dirs.append("/" + item + "/")
    return dirs

    
