#!/usr/bin/env python

from fsmdb import fsmdb

db = fsmdb.FsmDbSQLite("./test.db")
cols = ["test1", "test2", "test3"]
types = ["integer not null", "char", "long"]
db.create_table("test_table", cols, types)

