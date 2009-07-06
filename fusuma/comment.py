#!/usr/bin/env python
#######################################################################
# This file is part of Fusuma website management system.
#
# Copyright (c) hylom <hylomm at gmail.com>, 2008.
# 
# This file is released under the GPL.
#
# $Id:  $
#######################################################################

from bigblack import bigblack
from bigblack import bbtinydb
import time

class CommentCGI(bigblack.BigBlack):
    def __init__(self):
        super(CommentCGI,self).__init__()
        self.import_config("_database_name", key="database_name", validate=True, description="database's filename")
        self.import_config("_comment_tbl_name", key="comment_tbl_name", validate=True, description="name of table where comment is stored")

    def root(self):
        if self.param("op") != "add":
            self.error()
            return
        sid = self.param("sid")
        if self.param("state") == "show":
            state = 1
        else:
            state = 0
        name = self.param("name")
        email = self.param("email")
        ipaddr = self.param("REMOTE_ADDR")
        comment = self.param("comment")
        ret_url = self.param("ret_url")

        self.append_comment(sid=sid, state=state, name=name,
                            email=email, ipaddr=ipaddr, comment=comment)

        templ_param = dict(ret_url=ret_url)
        self.show_from_template("comment", "ok", templ_param)
        return 1

    def error(self):
        print self.http_header()
        print self.html_header(title="error")
        print self.html_body("<p>some error occured.</p>")

    def append_comment(self, sid="", state="0", date=time.time(), 
                       name="", email="", ipaddr="", comment=""):
        if comment == "" or ipaddr == "" or sid == "":
            return -1;

        comment_data = dict(sid=sid, state=state, date=date,
                            name=name, email=email, ipaddr=ipaddr,
                            comment=comment)
        db = self.get_database(self._database_name)
        db.insert(self._comment_tbl, comment_data)

    def standalone(self):
        self.check_config_all()
        db = self.get_database(self._database_name)
        print "checking database..."
        if not db.exists():
            print "database doesn't exists."
            self._create_table(db)
            print " -> create database: %s" % (self._database_name + ".db")
        else:
            print "databasae exists: %s." % (self._database_name + ".db")

        print "done."

    def _create_table(self, db):
#  cid      integer primary key autoincrement, /* comment ID */
#  sid      text not null,                  /* story ID */
#  state    integer default 0,              /* comment status */
#  date     real not null,                  /* post date */
#  name     text,                           /* poster's name */
#  email    text,                           /* email address */
#  ipaddr   text                            /* IP address */
#  comment  text not null,                  /* comment body */
        prototype = (
            ("cid", "integer primary key autoincrement"),
            ("sid", "text not null"),
            ("state", "integer default 0"),
            ("date", "real not null"),
            ("name", "text"),
            ("email", "text"),
            ("ipaddr", "text"),
            ("comment", "text not null")
            )
        db.create_table(self._comment_tbl_name, prototype)

cgi = CommentCGI()
cgi.run()

