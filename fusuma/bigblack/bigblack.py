#!/usr/bin/env python
#######################################################################
# bigblack.py - BigBlack the CGI Framework
#
# Copyright (c) hylom <hylomm at gmail.com>, 2009.
# 
# This file is released under the GPL.
#
#######################################################################
"""BigBlack: CGI Framework"""

import cgi
import sys
import os
import os.path

VERSION = "0.1.0"
VERSION_DATE = VERSION + " 06/16/2009"
VERSION_SPLIT = tuple(VERSION.split('.'))


class BigBlack(object):
    """BigBlack main class."""

    def __init__(self):
        """Creates the Backwall object."""

        self.load_config()

#### configuration functions
    def load_config(self, config_dir=""):
        """load config file.

        @param configfile: config file's directory
        @type configfile: string
        """

        if not config_dir:
            sys.path.insert(0,config_dir)
        from bbcfg import cfg as bb_cfg
        self._config = bb_cfg

    def get_config(self, key):
        return self._config[key]

    def get_config_with_default(self, key, default):
        return self._config.get(key, default)

    def import_config(self, attr, key, validate, description=""):
        """
        read config file, and validate, then regist as self's attribute.

        @param attr: attribute name append as self's attribute
        @type attr: string

        @param key: config's key
        @type key: string

        @param validate: if True, assert when key doesn't exist in config.
        @type validate: Bool
        """
        if not self._config.has_key(key):
            if validate:
                str = "config key '%s' doesn't exist. description: %s" % (key,description)
                raise Exception(str)
            setattr(self, attr, None)
        else:
            setattr(self, attr, self._config[key])

        try:
            self._imported[attr] = description
        except AttributeError:
            self._imported = {}
            self._imported[attr] = description

    def check_config_all(self):
        keys = []
        try:
            keys = self._imported
        except AttributeError:
            sys.stderr.write("no keys imported.\n")
            return

        sys.stderr.write("configuration for use:\n")
        for key in keys:
            desc = self._imported[key]
            sys.stderr.write("%s: %s\n" % (key, desc))

        sys.stderr.write("\n")
        
#### env/parameter access functions
    def param(self, key):
        """return CGI parameter.

        @param key: name of parameter
        @type key: string
        """

        if os.environ.get("METHOD") in ("GET", "POST"):
            return None;

        #FIXME: if form's value is large file?
        try:
            return self._form.getvalue(key)
        except AttributeError:
            self._form = cgi.FieldStorage()
            return self._form.getvalue(key)

    def path_info(self):
        """
        return PATH_INFO.
        """
        pathinfo = os.environ.get("PATH_INFO", "")
        if os.name == "nt":
            scriptname = getScriptname()
            if pathinfo.startswith(scriptname):
                pathinfo = pathinfo[len(scriptname):]
        return pathinfo

    def script_name(self):
        """
        return CGI's script name.
        """
        return os.environ.get("SCRIPT_NAME", "")

#### HTTP/HTML manipulation functions
    def html_body(self, content=""):
        return """<body>
%s
</body>
""" % content
        
    def http_header(self, ctype="text/html; charset=utf-8"):
        """
        return HTTP header.

        @param ctype="text.html": content-type string.
        @type ctype: string
        """
        return "Content-type: %s\n" %(ctype)

    def html_header(self, **headers):
        """
        return HTML header.

        @param headers={}: header parameters.
        @type headers: dict
        """
        header_string = "<html>\n<head>\n"

        for key in headers:
            header_string += "  <%s>%s</%s>\n" % (key,headers[key],key)

        header_string += "</head>\n<body>"
        return header_string

    def html_footer(self):
        """
        return HTML footer.
        """
        return "</body></html>"

    def html_redirection(self, url):
        """
        return redirection HTML code.

        @param url: redirection url
        @type url: string
        """
        return """<html>
  <head>
    <meta http-equiv="refresh" content="0;url=%s">
  </head>
</html>""" %(url)

#### cgi exection dispatcher functions
    def run(self):
        if os.environ.get("METHOD") in ("GET", "POST"):
            return self.dispatch()
        else:
            return self.standalone()

    def standalone(self):
        self.root()

    def dispatch(self):
        p = self.path_info()
        pathspec = p.split("/")
        if len(pathspec) > 1:
            func = pathspec[1]
            try:
                f = getattr(self, func)
                f()
            except AttributeError:
                self.fallback()
        else:
            self.root()

