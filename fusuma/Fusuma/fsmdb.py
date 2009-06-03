#!/usr/bin/env python
#######################################################################
# This file is part of Fusuma website management system.
#
# Copyright (c) hylom <hylomm at gmail.com>, 2008.
# 
# This file is released under the GPL.
#
#######################################################################
"""
This is Fusuma's database access module.
"""

__revision__ = "0.1"

VERSION = "0.0.1"
VERSION_DATE = VERSION + " 09/03/2008"
VERSION_SPLIT = tuple(VERSION.split('.'))

import sqlite3

class FsmDbError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class FsmDbOrderdDict(dict):
    """
    Orderd dictionary class for FsmDb.
    """
    def __init__(self, datas):
        """
        initialize.

        @param datas: list of tuples which contains key & values pair.
        @type datas: sequence
        """
        
        dict.__init__(self, datas)
        self.seq = [item[0] for item in datas]

    def keys(self):
        """ list of keys """
        return self.seq


class FsmDbSQLite(object):
    """
    This is FsmDb's main class.
    """
    def __init__(self, path_to_db):
        """
        initialize FsmDbSQLite.

        @param path_to_db: path to database
        @type path_to_db: string
        """
        self._path_to_db = path_to_db
        self._connection = None


    def _connect(self):
        if self._connection == None:
            self._connection = sqlite3.connect(self._path_to_db)


    def _cursor(self):
        self._connect()
        return self._connection.cursor()


    def _close_connect(self):
        if self._connection != None:
            self._connection.close()
            self._connection = None


    def close(self):
        self._close_connect()


    def begin(self):
        """begin transaction"""
        cur = self._cursor()
        cur.execute("""BEGIN TRANSACTION;""")
        cur.close()


    def commit(self):
        """commit transaction"""
        self._connection.commit()
        

    def select(self, table_name, expr=None):
        if expr != None:
            sql_cmd = "SELECT * FROM %s WHERE %s" % table_name
        else:
            sql_cmd = "SELECT * FROM %s" % table_name
        cur = self._cursor()
        cur.execute(sql_cmd)
        return cur
    

    def insert(self, table_name, param):
        """
        do insert with given paramater.

        @param table_name: name of table to create
        @type table_name: string

        @param param: paramater
        @type param: FsmDbOrderdDict
        """

        keys = param.keys()
        sql_cmd = """INSERT INTO "%s" (\n""" % table_name
        sql_cmd = sql_cmd + ",\n".join(keys) + "\n"
        sql_cmd = sql_cmd + ") VALUES (\n"
        sql_cmd = sql_cmd + ", ".join(("?",)*len(keys))
        sql_cmd = sql_cmd + ")"

        cur = self._cursor()
        t = tuple([param[key] for key in keys])

        cur.execute(sql_cmd, t)
        cur.close()


    def create_table(self, table_name, prototype):
        """
        create table to database.

        @param table_name: name of table to create
        @type table_name: string

        @param prototype: column and type data
        @type prototype: FsmDbOrderdDict
        """

        col_list = prototype.keys()
        type_list = [prototype[x] for x in col_list]

        self._create_table(table_name, col_list, type_list)


    def _create_table(self, table_name, col_list, type_list):
        """
        create table to database.

        @param table_name: name of table to create
        @type table_name: string

        """
        if len(col_list) != len(type_list):
            raise FsmDbError("len(col_list) isn't equal to len(type_list).")

        sql_cmd = "CREATE TABLE %s (\n" % table_name
        cmds = []
        for (column, type) in zip(col_list, type_list):
            cmds.append("  " + column + "\t" + type)

        sql_cmd = sql_cmd + ",\n".join(cmds) + "\n);"
        cur = self._cursor()

        # print sql_cmd

        cur.execute(sql_cmd)
        cur.close()
