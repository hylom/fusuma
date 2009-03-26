#!/usr/bin/env python
#######################################################################
# This file is part of Fusuma website management system.
#
# Copyright (c) hylom <hylomm at gmail.com>, 2008.
# 
# This file is released under the GPL.
#
# $Id: TemplateMan.py,v 1.6 2009/01/04 18:27:48 hylom Exp $
#######################################################################
"""
This is Fusuma's Template management module.
"""

__revision__ = "$Revision: 1.6 $"

import sys
import os
import re
from string import Template

VERSION = "0.0.1"
VERSION_DATE = VERSION + " 09/26/2008"
VERSION_SPLIT = tuple(VERSION.split('.'))



class TemplateMan(object):
    """
    This is Fusuma's template management class.
    """
    def get_template(self, template_name):
        """
        return template string.

        @param template_name: template name string
        @type template_name: string
        """
        if( template_name in self._template_of):
            templ = self._template_of[template_name]
            return Template( self._proc_macros(templ) )
        return Template("")

    def _proc_macros(self, string):
        """
        preprocess template macros.
        """
        return self._macro_insert.sub( self._proc_macro_insert, string )

    def _proc_macro_insert(self, matchobj):
        return self._template_of.get(matchobj.group(1), matchobj.group(0))

    def add_template(self, key, template):
        self._template_of[key] = template

    def __init__(self):
        """
        Initialize Template Manager.
        """

        template_of = {}
        self._macro_include = re.compile(r"\[%include\((.*?)\)%\]")
        self._macro_insert = re.compile(r"\[%insert\((.*?)\)%\]")

#const        
        template_of["story.html"] = """
<div class="article">
<h3><a name="${fn}">${title}</a></h3>
${body}
<div class="footer">
<span class="posted">[posted at ${ti}]</span>
path: <a href="${base_url}/${absolute_path_urlencoded}" title="path">/${absolute_path}</a>
<a href="${base_url}/${file_path_urlencoded}.${flavour}">permlink</a>
</div>
</div>
"""
        template_of["http_header"] = """Content-type: text/html; charset=utf-8;

"""

        template_of["html_header"] = """
<?xml version="1.0" encoding="UTF_8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
   "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
<head>
  <title>${title}</title>
  <meta http-equiv="content-script-type" content="text/javascript" />
  <meta http-equiv="Content-Style-Type" content="text/css" />
  ${heads}
</head>
<body>
"""

        template_of["html_footer"] = """
</body></html>
"""

        template_of["info_loginerror"] = """
<div class="login-error">
  <p>login error</p>
</div>
"""

        template_of["import_rss"] = """[%insert(http_header)%]
[%insert(html_header)%]
<hr>
${body}
<hr>
[%insert(html_footer)%]
"""

        template_of["filer"] = """[%insert(http_header)%]
[%insert(html_header)%]
<hr>
<form method="post" enctype="multipart/form-data" action="${SCRIPT_NAME}/filer/${file_rurl}">
<div class="create">
<input type="text" name="newfilename" class="newfilename" size="60" />
<input type="submit" name="op" value="newfile" />
<input type="submit" name="op" value="newdir" />
</div>
</form>

<hr>
${filer_body}
<hr>
[%insert(html_footer)%]
"""

        template_of["editor"] = """[%insert(http_header)%]
[%insert(html_header)%]
<hr>
<form method="post" enctype="multipart/form-data" action="${SCRIPT_NAME}/editor/${PATH}">
<div class="textarea">
<textarea name="text" class="text" cols="80" rows="20" wrap="soft">${text}</textarea>
</div>
<div class="buttons">
<input type="submit" name="op" value="save" />
</div>
</form>
<hr>
<a href="${FILER_URL}">back to filer</a>
[%insert(html_footer)%]
"""
#########################################################################
        template_of["editor_flavours"] = """[%insert(http_header)%]
[%insert(html_header)%]
<hr>
<form method="post" enctype="multipart/form-data" action="${SCRIPT_NAME}/editor_flavours/${PATH}">
<div class="textarea">
<textarea name="text" class="text" cols="80" rows="20" wrap="soft">${text}</textarea>
</div>
<div class="buttons">
<input type="submit" name="op" value="save" />
</div>
</form>
<hr>
<a href="${FILER_URL}">back to filer</a>
[%insert(html_footer)%]
"""

        template_of["editor_css"] = """[%insert(http_header)%]
[%insert(html_header)%]
<hr>
<form method="post" enctype="multipart/form-data" action="${SCRIPT_NAME}/editor_css/${PATH}">
<div class="textarea">
<textarea name="text" class="text" cols="80" rows="20" wrap="soft">${text}</textarea>
</div>
<div class="buttons">
<input type="submit" name="op" value="save" />
</div>
</form>
<hr>
<a href="${FILER_URL}">back to filer</a>
[%insert(html_footer)%]
"""
#########################################################################

        template_of["login"] = """[%insert(http_header)%]
[%insert(html_header)%]

<script type="text/javascript" src="/jq/jquery-1.3.2.min.js"></script>
<script type="text/javascript" src="/jq/jquery.sha1.js"></script>
<script type="text/javascript" src="/js/login.js"></script>

${error_message}

<div class="login-form">
  <form action="${SCRIPT_NAME}/login/" method="post" id="fsm-login-form">
    <input type="hidden" name="return_to" value="/" />
    <input type="hidden" name="login" value="1" />
    <input type="hidden" name="cr_id" value="${cr_id}" />
    <input type="hidden" name="cr_key" value="${cr_key}" />
    <input type="hidden" name="cr_auth" value="off" />

    <div id="login-form-loginname">
      <span>login:</span><input type="text" name="loginname" value="" />
    </div>

    <div id="login-form-password">
    <span>password:</span><input type="password" name="password" />
    </div>

    <div id="login-form-preserve">
    <span><input type="checkbox" id="preserve" name="preserve" /><label for="preserve">preserve login status</label></span>
    </div>

    <div id="login-form-usecr">
    <span><input type="checkbox" id="use_challenge" name="use_challenge" /><label for="use_challenge">use challenge &amp; responsepreserve auth.</label></span>
    </div>

    <div id="login-form-submit">
      <input type="submit" value="login" />
    </div>
  </form>
</div>

[%insert(html_footer)%]
"""

        template_of["login_succeed"] = """
<html>
<head>
<meta http-equiv="refresh" content="0;url=${url}">
</head>
</html>
"""

        template_of["root"] = """[%insert(http_header)%]
[%insert(html_header)%]
[%insert(header_bar)%]
[%insert(html_footer)%]
"""

        template_of["header_bar"] = """
<div id="header-bar">
  <ul>
    <li><span class="username">${user_name}</span></li>
    <li><a href="#" id="link-to-stories">stories</a></li>
    <li><a href="${SCRIPT_NAME}/new_story/" id="link-to-new-story">new story</a></li>
    <li><a href="#" id="link-to-settings">settings</a></li>
    <li><a href="${SCRIPT_NAME}/filer/" id="link-to-filer">filer</a></li>
    <li><a href="${SCRIPT_NAME}/filer_css/" id="link-to-filer">css editor</a></li>
    <li><a href="${SCRIPT_NAME}/filer_flavours/" id="link-to-filer">flavour editor</a></li>
    <li><a href="${SCRIPT_NAME}/fetch_rss/" id="link-to-logout">Fetch RSS</a></li>
    <li><a href="${SCRIPT_NAME}/lcomment/" id="link-to-lcomment">LiteComment</a></li>
    <li><a href="${SCRIPT_NAME}/logout/" id="link-to-logout">logout</a></li>
  </ul>
</div>
"""

        template_of["new_story"] = """[%insert(http_header)%]
[%insert(html_header)%]

${preview_html}

<div id="story-edit">
<form action="${SCRIPT_NAME}/new_story/" method="post">
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

        self._template_of = template_of

