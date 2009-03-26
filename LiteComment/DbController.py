#!/usr/bin/env python
#
#
"""
DbController.py  - Database Controller for Webpage comment system.
"""
import sys, os
import sqlite3
import time

VERSION = "0.0.1"
VERSION_DATE = VERSION + " 09/03/2008"
VERSION_SPLIT = tuple(VERSION.split('.'))


class DbController(object):
    """
    Database Controller for Webpage comment system.
    """
    def __init__(self, path_to_db):
        """
        Initializer - Do nothing.
        """
        self._path_to_db = path_to_db


    def create_db(self):
        """
        Create SQLite database file and create tables.

        @param path_to_db: A dict containing the configuration variables.
        @type path_to_db: string
        """
        sql_command1 = """
create table comment_table (
  cid      integer primary key autoincrement, /* comment ID */
  sid      text not null,                  /* story ID */
  cindex   integer not null,               /* comment index */
  state    integer default 0,              /* comment status */
  name     text,                           /* poster's name */
  comment  text not null,                  /* comment body */
  date     real not null,                  /* post date */
  email    text,                           /* email address */
  ipaddr   text                            /* IP address */
);"""

        sql_command2 = """
create table comment_index (
  sid     text primary key not null,  /* story ID */
  counter integer not null   /* number of comments */
);
"""

        #TODO: implement error routine.
        conn = sqlite3.connect( self._path_to_db )
        cur = conn.cursor()
        cur.execute("begin transaction;")
        cur.execute(sql_command1)
        cur.execute(sql_command2)
        cur.execute("end transaction;")
        conn.close()

    def list_all_comments( self, sid ):
        """
        list all comments of story specified by sid.
        returns cursor.

        @param sid: story id
        @type sid: string
        """

        sql_command = """
select * from comment_table where sid=? order by cindex;
"""
        sql_val = (sid,)

        conn = sqlite3.connect( self._path_to_db )
        cur = conn.cursor()
        cur.execute(sql_command, sql_val)

        result_list = []
        for row in cur:
            items = { "cid": row[0],
                      "sid": row[1],
                      "cindex": row[2],
                      "state": row[3],
                      "name": row[4],
                      "comment": row[5],
                      "date": row[6],
                      "email": row[7],
                      "ipaddr": row[8] }
            result_list.append(items)

#  cid      integer primary key autoincrement, /* comment ID */
#  sid      text not null,                  /* story ID */
#  cindex   integer not null,               /* comment index */
#  state    integer default 0,              /* comment status */
#  name     text,                           /* poster's name */
#  comment  text not null,                  /* comment body */
#  date     real not null,                  /* post date */
#  email    text,                           /* email address */
#  ipaddr   text                            /* IP address */

        conn.close()
        return result_list
        

    def insert_comment_at(self, sid, cindex, state, name, comment, datetime):
        """
        Insert new comment to given position.

        """
        
        sql_command = """
insert into comment_table values(  ?, ?, ?, ?, ?, ?, ?, ? );
"""
        datetime_str = ""

        sql_values = ( sid, cindex, state, name, comment, datetime_str )

        #TODO: implement error routine.
        conn = sqlite3.connect( self._path_to_db )
        cur = conn.cursor()
        cur.execute(sql_command, sql_values)

        conn.close()

    def number_of_comments(self, sid):
        sql_command = """
select counter from comment_index where sid=:sid;
"""
        conn = sqlite3.connect( self._path_to_db )
        cur = conn.cursor()
        cur.execute( sql_command, {"sid":sid} )

        res = cur.fetchall()
        conn.close()

        if len(res)  == 1:
            return res[0][0]
        return 0

    def append_comment(self, sid, state, name, comment, email, ipaddr):
        """
        Insert new comment to tail.
        """

        cindex = self.number_of_comments( sid )
        timestamp = time.time()

        sql_add_comment = """
insert into comment_table ( sid, cindex, state, name,
                            comment, date, email, ipaddr )
                    values( :sid, :cindex, :state, :name,
                            :comment, :date, :email, :ipaddr );
"""

        sql_update_comment = ""
        if cindex == 0:
            sql_update_comment = """
insert into comment_index(sid,counter) values( :sid, :counter );
"""
        else:
            sql_update_comment = """
update comment_index set counter=:counter where sid=:sid;
"""


        add_values = { "sid":sid,
                       "cindex":cindex, 
                       "state":state,
                       "name":name,
                       "comment":comment,
                       "date":timestamp,
                       "email":email,
                       "ipaddr":ipaddr }

        update_values = { "counter": cindex + 1,
                          "sid": sid }

        #TODO: implement error routine.
        conn = sqlite3.connect( self._path_to_db )
        cur = conn.cursor()

#        cur.execute("begin transaction;")
        cur.execute(sql_add_comment, add_values)
        cur.execute(sql_update_comment, update_values)
#        cur.execute(sql_update_comment)
#        cur.execute("commit;")

        conn.commit()
        conn.close()
