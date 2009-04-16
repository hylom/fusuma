#!/usr/bin/env python
#######################################################################
# tcgitools - Tiny CGI Tools
#
# Copyright (c) hylom <hylomm at gmail.com>, 2008.
# 
# This file is released under the GPL.
#
#######################################################################
"""
Tiny subroutines for CGI script.
"""

__revision__ = "$Revision: 1.2 $"

import cgi
import sys
import os
import re

VERSION = "0.0.1"
VERSION_DATE = VERSION + " 09/03/2008"
VERSION_SPLIT = tuple(VERSION.split('.'))

def escape_tags( str, accept_tags=[] ):
    """
    returns string.

    @param str: target string
    @type str: string

    @param accept_tags: accept tags
    @type accept_tags: list of string
    """

    if str == None:
        return None

#    str = str.replace( "&", "&amp;" )
    str = str.replace( "<", "&lt;" )
    str = str.replace( ">", "&gt;" )

    return str

class TCGI(object):
    """
    CGI access class.
    """

    def __init__(self):
        """
        build TCGITools class.
        """
        self._config = ""
        self._form = None;


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

    def env(self, key):
        """
        retrun environ variable's value.

        @param key: name of environ variable
        @type key: string
        """
        return os.environ.get(key, "")

    def param(self, key):
        """
        return param.

        @param key: 
        """
        if os.environ.get("METHOD") in ("GET", "POST"):
            return None;

        #TODO: if form's value is large file?

        try:
            return self._form.getvalue(key)
        except AttributeError:
            self._form = cgi.FieldStorage()
            return self._form.getvalue(key)

    def escaped_param( self, key, accept_tags=[]):
        """
        return escaped param.

        @param key: 
        """
        if os.environ.get("METHOD") in ("GET", "POST"):
            return None;

        return escape_tags( self.param(key), accept_tags )

    def http_header_content_type(self, ctype="text/html", ):
        """
        return HTTP header.

        @param ctype="text.html": content-type string.
        @type ctype: string
        """
        return "Content-type: %s" %(ctype)

    def http_header_end(self):
        """
        return end of HTTP header.
        """
        return ""

    def http_header(self, ctype="text/html", ):
        """
        return HTTP header.

        @param ctype="text.html": content-type string.
        """
        return "Content-type: %s\n" %(ctype)
    
    def xml_header(self):
       """
       return XML header.
       """
       return '<?xml version="1.0" encoding="utf-8"?>'

    def xml_footer(self):
       """
       return XML footer.
       """
       return ""

    def html_header(self, headers={}):
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
        return """
<html>
<head>
<meta http-equiv="refresh" content="0;url=%s">
</head>
</html>""" %(url)


