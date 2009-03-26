#!/usr/bin/env python
# -*- coding: utf-8 -*-
#######################################################################
# This file is part of Fusuma website management system.
#
# Copyright (c) hylom <hylomm at gmail.com>, 2008.
# 
# This file is released under the GPL.
#
# $Id:  $
#######################################################################

import os, sys, cgi
from datetime import datetime

is_cgi = 0
if os.environ.get("REQUEST_METHOD") in ("GET", "POST"):
    import cgitb; cgitb.enable()
    is_cgi = 1

# Settings are now in config.py, you should disable access to it by htaccess
# (make it executable or deny access)
from fusuma_cfg import fusuma as cfg

if cfg.has_key("fusuma_root"):
    sys.path.insert(0, cfg["fusuma_root"])
import TCGITools

if cfg.has_key("lcomment_root"):
    sys.path.insert(0, cfg["lcomment_root"])
import DbController


html_template_header = """<div class="lcomment-comment">
"""

html_template_spheader = """<div class="lcomment-comment">
  <span>state: %(state)d</span><br/>
  <span>%(cindex)s:#%(cid)d, </span>
  <span class="email">%(email)s, %(ipaddr)s</span>
"""

html_template = """  <span class="name">%(name)s</span>
  <span class="date">(%(date)s)</span><br/>
  <p class="comment_body">%(comment)s</p>
</div>
"""

def list_comments(mode, sid):
    """
    list up comments.

    @param mode: if show all comment, 1. else, 0
    @type mode: int

    @param sid: stort id
    @type sid: string
    """
    path_to_db = cfg["lcomment_path_to_db"]
    dbc = DbController.DbController( path_to_db )
    result_list = dbc.list_all_comments( sid )


#  cid      integer primary key autoincrement, /* comment ID */
#  sid      text not null,                  /* story ID */
#  cindex   integer not null,               /* comment index */
#  state    integer default 0,              /* comment status */
#  name     text,                           /* poster's name */
#  comment  text not null,                  /* comment body */
#  date     real not null,                  /* post date */
#  email    text,                           /* email address */
#  ipaddr   text                            /* IP address */

    template = ""
    if mode == 1:
        template = html_template_spheader + html_template
    else:
        template = html_template_header + html_template

    for item in result_list:
        if item["state"] > mode:
            continue;
        item["date"] = datetime.fromtimestamp(item["date"]).strftime("%Y-%m-%d %H:%M")
        item["name"] = TCGITools.escape_tags( item["name"], [] )
        item["comment"] = TCGITools.escape_tags( item["comment"], [] )
        item["email"] = TCGITools.escape_tags( item["email"], [] )
        print template % item

def run_as_cli():
    """
    lcomment.cgi <sid>
    """
    if len(sys.argv) < 1:
        print "lcomment.cgi <sid>"

    sid = sys.argv[1]
    list_comments(1, sid)


def ajax_preview():
    tcgi = TCGITools.TCGI()
    item = {}
    item["name"] = tcgi.escaped_param( "name" )
    item["comment"] = tcgi.escaped_param( "comment" )
    item["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")

#    item["name"] = "name"
#    item["comment"] = "hogehoge"

    template = html_template_header + html_template
    print tcgi.xml_header()
    print template % item
    print tcgi.xml_footer()
    
def ajax_submit():
    path_to_db = cfg["lcomment_path_to_db"]
    dbc = DbController.DbController( path_to_db )

    tcgi = TCGITools.TCGI()

    sid = tcgi.param("sid" )
    state = 0
    name = tcgi.escaped_param( "name" )
    item["comment"] = tcgi.escaped_param( "comment" )
    email = tcgi.escaped_param("email" )
    ipaddr = tcgi.env( "REMOTE_ADDR" )
    return_url = tcgi.env( "return_url" )
    mode = tcgi.env( "mode" )

    if tcgi.param("state" ) == "show":
        state = 1 

    dbc.append_comment(sid, state, name, comment, email, ipaddr)

    print tcgi.xml_header()
    print "<result>1</result>\n"
    print tcgi.xml_footer()

def cgi_list():

    path_to_db = cfg["lcomment_path_to_db"]
    dbc = DbController.DbController( path_to_db )

    tcgi = TCGITools.TCGI()

    print tcgi.http_header( "text/html; charset=utf-8")
    print tcgi.html_header( {"title":"test"} )

    sid = tcgi.param("sid" )
    state = 0
    name = tcgi.param( "name" )
    comment = tcgi.param( "comment" )
    email = tcgi.param("email" )
    ipaddr = tcgi.env( "REMOTE_ADDR" )
    return_url = tcgi.env( "return_url" )
    mode = tcgi.env( "mode" )

    if tcgi.param("state" ) == "show":
        state = 1 

    print "sid: %s<br>" % sid
    print "state: %s<br>" % state
    print "name: %s<br>" % name
    print "comment: %s<br>" % comment
    print "email: %s<br>" % email
    print "ipaddr: %s<br>" % ipaddr

    # for test
#sid = "qwerty"
#state = 1
#name = "namae"
#comment = "commmm"
#email = "a@b"
#ipaddr = "192."

    dbc.append_comment(sid, state, name, comment, email, ipaddr)

    print "transaction finished."
    print tcgi.html_footer()

def run_as_cgi():

    tcgi = TCGITools.TCGI()
    mode = tcgi.env( "mode" )

    if mode == "ajax_preview":
        ajax_preview()
    elif mode == "ajax_accept":
        ajax_submit()
    else:
        cgi_list()
    

############## main routine ################################

#test
#ajax_preview()

if is_cgi:
    run_as_cgi()
else:
    run_as_cli()
