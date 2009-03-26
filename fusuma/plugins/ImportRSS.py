#!/usr/bin/env python
#######################################################################
# This file is part of Fusuma website management system.
#
# Copyright (c) hylom <hylomm at gmail.com>, 2008.
# 
# This file is released under the GPL.
#
# $Id: Fusuma.py,v 1.6 2009/01/04 18:27:48 hylom Exp $
#######################################################################
"""
This is Fusuma's RSS import plugin.
"""

__revision__ = "$Revision: 1.0 $"

import cgi
import sys
import os
from stat import *
import Cookie
import datetime
import time
import locale
import dircache
import re

import TCGITools
import PasswordMan
import BackWall
from SessionMan import SessionMan
from TemplateMan import TemplateMan

VERSION = "0.0.1"
VERSION_DATE = VERSION + " 01/18/2009"
VERSION_SPLIT = tuple(VERSION.split('.'))

def fsm_add_handlers(fsm):
    regex = re.compile(r"^/fetch_rss/")
    fsm.append_url_handler( regex, url_handler )

def url_handler(fsm):
    args = dict( title = "import RSS",
                 body = "",
                 )

    command = fsm.get_config( "fetch_rss_cmd" )
    child = os.popen(command)
    data = child.read()
    err = child.close()

    if err:
        data = "error occued!\n" + data

    data = data.replace( "\n", "<br>" )

    args["body"] = data
    print fsm.parse_template( "import_rss", args )
