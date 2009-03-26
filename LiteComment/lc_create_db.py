#!/usr/bin/env python

import sys, os
import sqlite3
import DbController

db = DbController.DbController("./comment.db")
#db = DbController.DbController(":memory:")
db.create_db()
#db.append_comment( "qwerty", 1, "namae", "hogehoge", "test@hoge", "192.16.1.1" )


