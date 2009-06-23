#!/usr/bin/env python
#######################################################################
# This file is part of Fusuma website management system.
#
# Copyright (c) hylom <hylomm at gmail.com>, 2008.
# 
# This file is released under the GPL.
#
# $Id: BackWall.py,v 1.1 2008/12/15 12:24:03 hylom Exp $
#######################################################################
"""
BackWall: CGI Framework
"""

__revision__ = "$Revision: 1.1 $"

import cgi
import sys
import os
import os.path
import Cookie
import datetime
import locale

import TCGITools
import PasswordMan
from SessionMan import SessionMan
from TemplateMan import TemplateMan
import fsmdb

VERSION = "0.0.1"
VERSION_DATE = VERSION + " 09/03/2008"
VERSION_SPLIT = tuple(VERSION.split('.'))


class BackWall(TCGITools.TCGI):
    """
    BackWall main class.
    """
    def __init__(self, config, environ):
        """
        Sets configuration and environment.
        Creates the Backwall object.

        @param config: A dict containing the configuration variables.
        @type config: dict

        @param environ: A dict containing the environment variables.
        @type environ: dict
        """
        super(BackWall, self).__init__()
#        self._config = ""
#        self._form = None;

        self._config = config
        self._env = environ
        self._session_man = SessionMan( database_dir=self._config["session_objs_dir"] )
        self._template_man = TemplateMan()
        self._context_args = dict( os.environ, heads = "" )

    def get_database(self, database):
        db_path = os.path.join(self.get_config_safe("database_dir"), database + ".db")
        db = fsmdb.FsmDbSQLite(db_path)
        return db;

    def get_config_safe(self, key):
        return self._config[key]

    def get_config(self, key, default=""):
        return self._config.get( key, default )

    def add_template(self, key, template):
        self._template_man.add_template( key, template )

    def get_template(self, strTemplate):
        return self._template_man.get_template(strTemplate)

    def parse_template(self, strTemplate, dictMap):
        args = dict( self._context_args )
        args.update( dictMap )
        try:
            return self._template_man.get_template(strTemplate).safe_substitute(args)
        except AttributeError:
            return ""

    def add_template(self, key, template):
        self._template_man.add_template(key, template)

    def get_context_args(self):
        return self._context_args

    def set_py_cfg(self, py_cfg):
        self._py_cfg = py_cfg

    def get_py_cfg(self, key, default=""):
        return self._py_cfg.get(key, default)

    def session(self):
        """
        return current session.
        """
        try:
            return self._session
        except AttributeError:
            self._session = self.get_session()
            return self._session

    def get_session(self):
        """
        get session from HTTP_COOKIE.
        """
        if self._env["HTTP_COOKIE"] != "" :
            ck = Cookie.SimpleCookie(self._env['HTTP_COOKIE'] )
            if ck.has_key("fsmsid"):
                session = self.get_session_man().get_session_from_id(ck["fsmsid"].value)
                return session
        return None
                
# getter/setter
    def get_session_man(self):
        """
        return SessionMan object.
        """
        return self._session_man

