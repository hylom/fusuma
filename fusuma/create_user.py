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

import os
import sys
import sqlite3
import getpass
import getopt

from Fusuma import PasswordMan
from fusuma_cfg import fusuma as cfg

opt_list, args = getopt.getopt( sys.argv[1:], "o:", ["debug"] )
path_to_db = cfg["path_to_users_db"]
_DEBUG = 0
for opt,arg in opt_list:
	if opt == "-o":
		path_to_db = arg
	if opt == "--debug":
		_DEBUG = 1

if _DEBUG:
	uname = "test"
	str_seclv = "10"
	comment = "test user"
	passwd = "hogehoge"
else:
	try:
		uname = raw_input("user name: ")
		str_seclv = raw_input("seclv (int): ")
		comment = raw_input("comment: ")
		passwd = getpass.getpass("login password: ")
	except KeyboardInterrupt:
		sys.exit("\nabort.")

if not str_seclv.isdigit():
	sys.exit("seclv must be integer.")

seclv = int(str_seclv)

# hashed_passwd = hashlib.sha256(passwd).hexdigest()
# hashed_passwd = sha.new(passwd).hexdigest()

pwm = PasswordMan.PasswordMan(path_to_db)

if not os.path.exists( path_to_db ):
	pwm.create_db()

if not os.path.isfile( path_to_db ):
	sys.exit( "cannot create database!\n" )

pwm.add_user(uname, passwd, seclv, comment)

sys.stderr.write("add %s.\n" % uname)


