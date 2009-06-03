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
This is Fusuma's main module.
"""

__revision__ = "$Revision: 1.6 $"

import cgi
import sys
import os
import os.path
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
VERSION_DATE = VERSION + " 09/03/2008"
VERSION_SPLIT = tuple(VERSION.split('.'))


class Fusuma(BackWall.BackWall):
    """
    This is Fusuma's main class.
    """
    def __init__(self, config, environ):
        """
        Sets configuration and environment.
        Creates the L{Request} object.

        @param config: A dict containing the configuration variables.
        @type config: dict

        @param environ: A dict containing the environment variables.
        @type environ: dict
        """
        super(Fusuma, self).__init__(config, environ)
        self.url_handler = [];

    def regist_plugins(self):
        """
        Regist plugins.
        """
        path_plugin_dir = self.get_config("plugin_dir")
        sys.path.insert( 0, path_plugin_dir )

        if not os.path.isdir(path_plugin_dir):
            return

        filenames = dircache.listdir( path_plugin_dir )
        for filename in filenames:
            file_path = os.path.join( path_plugin_dir, filename )

            if not os.path.isfile(file_path):
                continue

            if re.search( r"\.py$", filename ):
                module_name = re.sub( r"\.py$", "", filename)
                if module_name == "plugin":
                    continue
                module = __import__(module_name)
                module.fsm_add_handlers(self)

    def append_url_handler( self, regex, func ):
        """
        Append URL Hander.
        """
        self.url_handler.append( (regex, func ) )

    def run(self):
        """
        This is Fusuma's main routine.
        """

#        print "Content-type: text/html;\n\n"

#        if self.path_info() == "/do_login/":
#            self._do_login()
#            return

#        session = self.session()
        if( self.session() == None ):
            self._login(self)
            return

        self.regist_plugins()

        # regist handlers
        self.url_handler.append( (re.compile(r"^/login/"), self._login ) )
        self.url_handler.append( (re.compile(r"^/logout/"), self._logout) )

        for (regex, func) in self.url_handler:
            if regex.search( self.path_info() ):
                func(self)
                break
        else:
            self._root()                
        

##############################################################

    def _root(self):
        """
        Handler for http://server.name/<cgi_pathname>
        """
 #       print self.http_header("text/html; charset=utf-8;")
        template_args = dict( title = "fsm",
                              user_name = self.session().value_from_key("loginname")
                              )
        print self.parse_template( "root", template_args )

    def _logout(self, fsm):
        """
        delete session.
        """
        session = self.session()

        lname = session.value_from_key("loginname")
        ck = Cookie.SmartCookie()
        ck["fsmsid"] = session.sid()
        ck["fsmsid"]["path"] = self.script_name()
        dt_expire = datetime.datetime.today() - datetime.timedelta( days = 7 )
        current_locale = locale.getlocale( locale.LC_CTYPE )
        locale.setlocale( locale.LC_CTYPE, "" )
        ck["fsmsid"]["expires"] = dt_expire.strftime( "%a, %d-%b-%Y %H:%M:%S GMT" )
        locale.setlocale( locale.LC_CTYPE, current_locale )

        print self.http_header_content_type("text/html; charset=utf-8;")
        print ck
        print self.http_header_end()
        print self.html_redirection( self.script_name() )

        session.delete()

    def _login(self, fsm):
        """
        check username & password, and connect session.
        """

        loginname = self.param("loginname")
        passwd = self.param("password")
        cr_id = self.param("cr_id")
        cr_key = self.param("cr_key")
        cr_auth = self.param("cr_auth")

        if (loginname == None) or (loginname == ""):
            self._login_error()
            return
        if passwd == None:
            passwd = ""

        pwman = PasswordMan.PasswordMan(self.get_config("path_to_users_db"), self.get_config("temp_dir"))

        if cr_auth == "on":
            userId = pwman.get_userId_with_cr(loginname, passwd, cr_id)
        else:
            userId = pwman.get_userId(loginname, passwd)

        if userId < 0:
            self._login_error()
            #print "login:" + loginname + " passwd:" + passwd
            return
        else:
            self._login_succeed()

    def _login_error(self):
        """
        show login error message.
        """

  #      print self.http_header("text/html; charset=utf-8;")
        # create challenge id & key
        pwman = PasswordMan.PasswordMan( self.get_config("path_to_users_db"), self.get_config("temp_dir") )
        (id, key) =  pwman.challenge_key()
        template_args = {"title":"fsm login",
                         "error_message":"",
                         "cr_id":id,
                         "cr_key":key,
                         }
        print self.parse_template( "login", template_args )


    def _login_succeed(self):
        """
        show login succeed message.
        """
        is_preserve = self.param("preserve")

        ck = Cookie.SmartCookie()
        sman = self.get_session_man()
        session = sman.new_session( self.param("loginname") )

        ck["fsmsid"] = session.sid()
        ck["fsmsid"]["path"] = self.script_name()

        if is_preserve:
            dt_expire = datetime.datetime.today() + datetime.timedelta( days = 7 )
            current_locale = locale.getlocale( locale.LC_CTYPE )
            locale.setlocale( locale.LC_CTYPE, "" )
            ck["fsmsid"]["expires"] = dt_expire.strftime( "%a, %d-%b-%Y %H:%M:%S GMT" )
            locale.setlocale( locale.LC_CTYPE, current_locale )
            # format of expires is "Thu, 1-Jan-2030 00:00:00 GMT"
            session.add_object( "expire", dt_expire.isoformat() )

#        ck["fsmsid"]["domain"] = self.script_name();

        session.add_object( "loginname", self.param("loginname") )
        session.save()

        print ck
        print self.http_header_content_type("text/html; charset=utf-8;")
        print self.http_header_end()

        template_args = dict( url = self.script_name() )
        print self.parse_template( "login_succeed", template_args )



#
# command line usage
#

USAGE = """Syntax: %(script)s [path-opts] [args]
"""
