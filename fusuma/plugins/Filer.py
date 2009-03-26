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
    fsm.append_url_handler( re.compile(r"^/filer/"), _filer )
    fsm.append_url_handler( re.compile(r"^/editor/"), _editor )

def _editor(self):
    """
    Handler for http://server.name/<cgi_pathname>/editor/
    """
    root_fullpath = self.get_config( "file_root" )
    root_url = self.script_name() + "/editor/"
    file = self.path_info().replace( "/editor/", "" )
    file_fullpath = os.path.join( root_fullpath, file )

    root_filer = self.script_name() + "/filer/"
    filer_url = root_filer + os.path.dirname(file)

    op = self.param("op")

    if op == "save":
        text = self.param("text")
        file_obj = open( file_fullpath, 'w' )
        file_obj.write(text)
        file_obj.close()

    file_obj = open( file_fullpath, 'r' )
    file_content = file_obj.read()
    file_obj.close()

    args = dict( title = "edit",
                 preview_html = "",
                 text = file_content,
                 PATH = file,
                 FILER_URL = filer_url,
                 )
        
    print self.parse_template( "editor", args )
            
def _viewer(self):
    """
    Handler for http://server.name/<cgi_pathname>/viewer/
    """
    root_fullpath = self.get_config( "file_root" )
    root_url = self.script_name() + "/viewer/"
    current_dir = self.path_info().replace( "/viewer/", "" )
    current_fullpath = os.path.join( root_fullpath, current_dir )

def _filer(self):
    """
    Handler for http://server.name/<cgi_pathname>/filer/
    """

    root_fullpath = self.get_config( "file_root" )
    root_url = self.script_name() + "/filer/"
    viewer_url = self.script_name() + "/viewer/"
    editor_url = self.script_name() + "/editor/"

    current_dir = self.path_info().replace( "/filer/", "" )
    current_fullpath = os.path.join( root_fullpath, current_dir )

    if ( not os.access( current_fullpath, os.R_OK ) ):
        print self.http_header()
        print "<html><body>error: no accessable permittion.</body></html>"
        return

    if self.param("op") == "newfile":
        filename = self.param("newfilename")
        if re.compile("[^A-Za-z0-9+_-]").match(filename):
            filename = ""
        if filename != "" :
            file_path = os.path.join( current_fullpath, filename )
            file_obj = open( file_path, 'w' )
            file_obj.close()
    elif self.param("op") == "newdir":
        filename = self.param("newfilename")
        if re.compile("[^A-Za-z0-9+_-]").match(filename):
            filename = ""
        if filename != "" :
            file_path = os.path.join( current_fullpath, filename )
            os.mkdir( file_path )
        
    format = '''
<span class="file-item">
<span class="type"><a href="%(href_viewer)s">%(type)s</a></span>
<span class="filename"><a href="%(href_viewer)s">%(filename)s</a></span>
<span class="size">%(size)s</span>
<span class="uid">%(uid)s</span>
<span class="gid">%(gid)s</span>
<span class="mtime">%(mtime)s</span>
<span class="link-edit"><a href="%(href_editor)s?op=edit">[edit]</a></span>
<span class="link-delete"><a href="%(href_filer)s?op=del">[delete]</a></span>
<span class="link-rename"><a href="%(href_filer)s?op=ren">[rename]</a></span>

</span><br>
'''
    header = '''
[ <a href="%s">/</a> ] %s<br>
<span class="file-item">
<span class="type">type</span>
<span class="filename">filename</span>
<span class="size">size</span>
<span class="uid">uid</span>
<span class="gid">gid</span>
<span class="mtime">mtime</span>
</span><br>
''' % (root_url, current_dir)

    dirs_list = dircache.listdir(current_fullpath)
    file_list = list( header )
    for file in dirs_list:
        file_path = os.path.join( current_fullpath, file )
        stat_info = os.stat( file_path )
        file_info = { "filename": file,
                      "size": stat_info.st_size,
                      "uid": stat_info.st_uid,
                      "gid": stat_info.st_gid,
                      }
        file_info['mtime'] = time.strftime("%y-%m-%d %H:%M:%S",time.localtime(stat_info.st_mtime) )
        if ( S_ISDIR(stat_info[ST_MODE]) ):
            file_info['type'] = "[dir]"
            href_filer = os.path.join(root_url, current_dir, file)
            href_editor = os.path.join(editor_url, current_dir, file)
            file_info["href_viewer"] = href_filer
            file_info["href_filer"] = href_filer
            file_info["href_editor"] = href_editor
        else:
            file_info['type'] = "[file]"
            href_filer = os.path.join(root_url, current_dir, file)
            href_editor = os.path.join(editor_url, current_dir, file)
            href_viewer = os.path.join(viewer_url, current_dir, file)
            file_info["href_viewer"] = href_viewer
            file_info["href_filer"] = href_filer
            file_info["href_editor"] = href_editor

        str = format % file_info
        file_list.append( str )

    files = "".join(file_list)

    args = dict( title = "filer",
                 preview_html = "",
                 filer_body = files,
                 file_rurl = current_dir,
                 )
    print self.parse_template( "filer", args )

