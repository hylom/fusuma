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
import pickle
import random
from datetime import datetime

VERSION = "0.0.1"
VERSION_DATE = VERSION + " 09/26/2008"
VERSION_SPLIT = tuple(VERSION.split('.'))


class AuthError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class PasswordMan(object):
    """
    This is Fusuma's account management class.
    """
    def __init__(self, path_to_db="", tmp_dir=""):
        """
        Initialize Password Manager.
        """
        self._path_to_db = path_to_db
        self._tmp_dir = tmp_dir

    def get_userId(self, username, passwd):
        """
        if username and password are validated, return userId.

        @param username: username string
        @type username: string

        @param passwd: password string
        @type passwd: string
        """

        try:
            result = self._query_from_username(username)
        except AuthError:
            return -1

        if result["passwd"] == self._hash_passwd(passwd):
                return result["uid"]
        else:
            return -1
            
    def _query_from_username(self, username):
        """
        do query to database.
        """
        sql_select_user = """
select * from users_table where uname = ? ;
"""

        # integrity check
        if re.search(r"[^A-Za-z0-9_]", username):
            raise AuthError("UserNotFound")

        try:
            conn = sqlite3.connect( self._path_to_db )
            cur = conn.cursor()
            cur.execute(sql_select_user, (username,) )
        except sqlite3.OperationalError:
            raise AuthError("sqlite3error")
            

        # 1|test|4c716d4cf211c7b7d2f3233c941771ad0507ea5bacf93b492766aa41ae9f720d|10|test
        datas = cur.fetchone()
        conn.close()

        if datas:
            result = { "uid":datas[0],
                       "uname":datas[1],
                       "passwd":datas[2],
                       "seclv":datas[3],
                       "comment":datas[4] }
            return result
        else:
            raise AuthError("UserNotFound")


    def get_userId_with_cr(self, username, response, cr_id):
        """
        if username and password are validated, return userId.

        @param username: username string
        @type username: string

        @param response: password string
        @type response: string

        @param cr_id: challenge & responce ID
        @type cr_id: string
        """

        try:
            result = self._query_from_username(username)
        except AuthError:
            return -1

        #### DEBUG ####
        #print "Content-type: text/html;\n\n"
        #print "username, response, cr_id, <br>"
        #print username, response, cr_id, "<br>"
        ####

        if self.check_response(cr_id, response, result["passwd"]) == 1:
            return result["uid"]
        else:
            return -1


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

        # TODO: implement error routine.
        print self._path_to_db
        conn = sqlite3.connect( self._path_to_db )
        cur = conn.cursor()
        #cur.execute("begin transaction;")
        cur.execute(sql_command1)
        #cur.execute("end transaction;")
        conn.close()


    def challenge_key(self):
        """
        generate challenge_key.
        """
        auth_list = self._load_auth_list()
        random.seed(datetime.now())
        id = random.randint(0,65536)
        while id in auth_list:
            id = random.randint(0, 65536)

        key = random.randint(0, 2147483646)
        auth_list[str(id)] = str(key)

        self._save_auth_list(auth_list)
        return (id, key)


    def _save_auth_list(self, auth_list):
        path_to_auth = os.path.join(self._tmp_dir, "auth.dat")
        file_auth = open(path_to_auth, "w")
        pickle.dump(auth_list, file_auth)
        file_auth.close()


    def _load_auth_list(self):
        path_to_auth = os.path.join(self._tmp_dir, "auth.dat")
        if os.path.exists(path_to_auth):
            try:
                file_auth = open( path_to_auth, "r")
                auth_list = pickle.load(file_auth)
            except PickleError:
                auth_list = {}
            file_auth.close()
        else:
            auth_list = {}
        return auth_list


    def check_response(self, id, response, passwd):
        """
        verify response.

        @param id: challenge id
        @type id: int

        @param response: response string value
        @type response: string

        @param passwd: hashed correct passwd
        @type passwd: string
        """
        auth_list = self._load_auth_list()
        key = auth_list.get(str(id), "")
        if key == "":
            return 0

        del auth_list[str(id)]
        self._save_auth_list(auth_list)

        correct_key = self._hash_passwd(str(key) + passwd)

        ####
        #print "key, passwd, correct_key, <br>"
        #print key, passwd, correct_key, "<br>"
        ####
        if response == correct_key:
            return 1
        else:
            return 0


    def _hash_passwd(self, passwd):
        return hashlib.sha1(passwd).hexdigest()
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

        # TODO: implement error routine.
        conn = sqlite3.connect( self._path_to_db )
        cur = conn.cursor()

        cur.execute(sql_add_user, add_values)

        conn.commit()
        conn.close()

