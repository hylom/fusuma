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

VERSION = "0.0.1"
VERSION_DATE = VERSION + " 01/18/2009"
VERSION_SPLIT = tuple(VERSION.split('.'))

import re
import Fusuma
import extentions.lcomment

def fsm_add_handlers(fsm):
    fsm.append_url_handler( re.compile(r"^/lcomment/"), main_handler )
    template_root = """[%insert(http_header)%]
[%insert(html_header)%]
<hr>
<h2>Regist comment:</h2>

<form method="post" enctype="multipart/form-data" action="${lcomment_url}">
<div class="add-comment">
sid:<input type="text" name="sid" class="lcomment_sid" size="30" /><br/>
name:<input type="text" name="name" class="lcomment_name" size="60" />
<select name="state" class="lcomment_state" >
  <option value="hidden">hidden</option>
  <option value="show" selected >show</option>
</select><br/>
email:<input type="text" name="email" class="lcomment_email" size="60" /><br/>
<textarea name="comment" class="lcomment_comment" cols="80" rows="10" wrap="soft"></textarea><br/>

return url:<input type="text" name="ret_url" class="lcomment_ret_url" size="60" />

<input type="submit" name="op" value="add" />
</div>
</form>

<hr>
<h2>Show comment:</h2>

<form method="get" action="${lcomment_url}">
<div>
sid:<input type="text" name="sid" />
<input type="submit" name="op" value="show" />
</div>
</form>

<hr>
[%insert(html_footer)%]
"""
    fsm.add_template( "LiteComment_root", template_root )


def main_handler(fsm):
    """
    Handler for http://server.name/<cgi_pathname>/lcomment/
    """
    url_basedir = re.sub( r"fsm\.py$", "", fsm.script_name() )
    args = dict( title = "edit",
                 lcomment_url = url_basedir + "comment.py",
                 )

    if fsm.param("op") == "add":
        add(fsm)
    elif fsm.param("op") == "show":
        show(fsm)
    else:
        print fsm.parse_template( "LiteComment_root", args )

def add(fsm):
    sid = fsm.param("sid")
    if fsm.param("state") == "show":
        state = 1
    else:
        state = 0
    name = fsm.param("name")
    email = fsm.param("email")
    ipaddr = fsm.param("REMOTE_ADDR")
    comment = fsm.param("comment")

    lwc = lcomment.LWComment(fsm)
    lwc.append_comment(sid=sid, state=state, name=name,
                       email=email, ipaddr=ipaddr, comment=comment)

