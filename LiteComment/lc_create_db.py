#!/usr/bin/env python

import sys, os
import sqlite3
import DbController

db = DbController.DbController("./comment.db")
#db = DbController.DbController(":memory:")
db.create_db()
#db.append_comment(sid="qwerty", state=1, name="namae", comment="hogehoge", email="test@hoge", ipaddr="192.16.1.1")

