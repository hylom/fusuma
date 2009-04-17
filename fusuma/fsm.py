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

import os, sys


# this allows for a config.py override
script = os.environ.get('SCRIPT_FILENAME', None)
if script is not None:
    script = script[0:script.rfind("/")]
    sys.path.insert(0, script)

# this allows for grabbing the config based on the DocumentRoot
# setting if you're using apache
root = os.environ.get('DOCUMENT_ROOT', None)
if root is not None:
    sys.path.insert(0, root)

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

if __name__ == '__main__':
    env = {}

# run as a regular CGI

    if os.environ.get("REQUEST_METHOD") in ("GET", "POST"):
        import cgitb; cgitb.enable()

    for mem in ["HTTP_HOST", "HTTP_USER_AGENT", "HTTP_REFERER",
                "PATH_INFO", "QUERY_STRING", "REMOTE_ADDR",
                "REQUEST_METHOD", "REQUEST_URI", "SCRIPT_NAME",
                "HTTP_IF_NONE_MATCH", "HTTP_IF_MODIFIED_SINCE",
                "HTTP_COOKIE", "CONTENT_LENGTH", "CONTENT_TYPE",
                "HTTP_ACCEPT", "HTTP_ACCEPT_ENCODING"]:
        env[mem] = os.environ.get(mem, "")

    f = Fusuma(cfg, env)
    f.set_py_cfg(py_cfg)
    f.run()

