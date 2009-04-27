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

    def create_table(self, table_name, col_list, type_list):
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

        print sql_cmd

        cur.execute(sql_cmd)
        cur.close()

