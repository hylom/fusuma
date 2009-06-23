#!/usr/bin/env python
##################################################
# This file is part of Fusuma website management system.
# Copyright (c) hylom <hylomm at gmail.com>, 2008.
# This file is released under the GPL.
#
# fsmman.py: Fusuma manager
#
# Fusuma manager is command line interface to use
# for maintain Fusuma system.
##################################################
import os
import sys

# this allows for a config.py override
script = os.environ.get('SCRIPT_FILENAME', None)
if script != None:
    script = script[0:script.rfind("/")]
    sys.path.insert(0, script)

# Settings are now in config.py, you should disable access to it by htaccess
# (make it executable or deny access)
from fusuma_cfg import fusuma as cfg

if cfg.has_key("config_py"):
    sys.path.insert(0,cfg["config_py"])
from config import py as py_cfg

# If the user defined a "codebase" property in their config file,
# then we insert that into our sys.path because that's where the
# PyBlosxom installation is.
if cfg.has_key("fusuma_root"):
    sys.path.insert(0, cfg["fusuma_root"])

from Fusuma import Fusuma

from extentions.lcomment import LWComment

def usage():
    print """usage: %s lcomment <subcommand> [opt...]""" % sys.argv[0]

def lcomment_usage():
    print """usage: %s lcomment createdb <path>""" % sys.argv[0]

def lcomment_createdb(fsm):
    db = fsm.get_database("lcomment")
    
    
env = {}
fsm = Fusuma(cfg, env)
fsm.set_py_cfg(py_cfg)

try:
    mode = sys.argv[1]
except IndexError:
    usage()
    sys.exit()

if mode == "lcomment":
    try:
        act = sys.argv[2]
    except IndexError:
        lcomment_usage()
        sys.exit()
    if act == "createdb":
        lwc = LWComment(fsm)
        lwc.db_create_table()
    else:
        lcommen_usage()


