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

import bigblack

class CommentCGI(bigblack.BigBlack):
    def __init__(self):
	self._database = "lcomment"
        self._comment_tbl = "comment"

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

    def append_comment(self, sid="", state="0", date=time.time(), 
                       name="", email="", ipaddr="", comment=""):
        if comment == "" or ipaddr == "" or sid == "":
            return -1;

        comment_data = dict(sid=sid, state=state, date=date,
                            name=name, email=email, ipaddr=ipaddr,
                            comment=comment)
        db = self.get_database(self._database)
        db.insert(self._comment_tbl, comment_data)


cgi = CommentCGI()
cgi.run()

