#!/usr/bin/env python
#######################################################################
# This file is part of Fusuma website management system.
#
# Copyright (c) hylom <hylomm at gmail.com>, 2008.
# 
# This file is released under the GPL.
#
# $Id: PasswordMan.py,v 1.1.1.1 2008/11/27 17:15:37 hylom Exp $
#######################################################################
"""
This is Fusuma's account management module.
"""

__revision__ = "$Revision: 1.1.1.1 $"

import cgi
import sys
import os
import sqlite3
import re
import hashlib


VERSION = "0.0.1"
VERSION_DATE = VERSION + " 09/26/2008"
VERSION_SPLIT = tuple(VERSION.split('.'))


class PasswordMan(object):
    """
    This is Fusuma's account management class.
    """
    def __init__(self, path_to_db=""):
        """
        Initialize Password Manager.
        """
        self._path_to_db = path_to_db


    def get_userId(self, username, passwd):
        """
        if username and password are validated, return userId.

        @param username: username string
        @type username: string

        @param passwd: password string
        @type passwd: string
        """

        sql_select_user = """
select * from users_table where uname = ? ;
"""

        # integrity check
        if re.search(r"[^A-Za-z0-9_]", username):
            return -1

        # TODO: implement error routine.

        print "> ", self._path_to_db

#        try:
        conn = sqlite3.connect( self._path_to_db )
        cur = conn.cursor()
        cur.execute(sql_select_user, (username,) )
#        except sqlite3.OperationalError:
            

        # 1|test|4c716d4cf211c7b7d2f3233c941771ad0507ea5bacf93b492766aa41ae9f720d|10|test
        datas = cur.fetchone()
        conn.close()

        if datas:
            hashed_passwd = self._hash_passwd(passwd)
            uid = datas[0]
#            uname = datas[1]
            passwd = datas[2]
#            seclv = datas[3]
#            comment = datas[4]
            if passwd == hashed_passwd:
                return uid
            else:
                return -1
            
        else:
            return -1


#        # root only!
#        if (username == "hylom") and (passwd == "stringer"):
#            return 1
#        else:
#            return -1


    def create_db(self):
        """
        Create SQLite database file and create tables.

        """
        sql_command1 = """
create table users_table (
  cid      integer primary key autoincrement, /* user ID */
  uname    text not null,                     /* user name */
  upasswd  text,                              /* hashed passwd */
  seclv    integer not null,                  /* user's security level */
  comment  text                               /* comment */
);"""

        #TODO: implement error routine.
        print self._path_to_db
        conn = sqlite3.connect( self._path_to_db )
        cur = conn.cursor()
        cur.execute("begin transaction;")
        cur.execute(sql_command1)
        cur.execute("end transaction;")
        conn.close()

    def _hash_passwd(self, passwd):
        return hashlib.sha256(passwd).hexdigest()
        # hashed_passwd = sha.new(passwd).hexdigest()

    def add_user(self, uname, upasswd, seclv, comment):
        """
        add new user.
        """

        sql_add_user = """
insert into users_table ( uname, upasswd, seclv, comment )
                   values( :uname, :upasswd, :seclv, :comment );
"""
        hashed_passwd = self._hash_passwd(upasswd)

        add_values = { "uname":uname,
                       "upasswd":hashed_passwd, 
					   "seclv":seclv,
					   "comment":comment }

        #TODO: implement error routine.
        conn = sqlite3.connect( self._path_to_db )
        cur = conn.cursor()

        cur.execute(sql_add_user, add_values)

        conn.commit()
        conn.close()

