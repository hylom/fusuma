#!/usr/bin/env python
# -*- coding: utf-8 -*-
#######################################################################
# This file is part of Fusuma website management system.
#
# Copyright (c) hylom <hylomm at gmail.com>, 2008.
# 
# This file is released under the GPL.
#
# $Id: TwHeadLine.py,v 1.2 2009/01/13 17:14:13 hylom Exp $
#######################################################################

import os, sys, re, locale
from os.path import *
import dircache
from datetime import datetime,timedelta

if len(sys.argv) < 2:
    sys.exit( "usage: %s <directory> " % sys.argv[0] )

basedir = sys.argv[1]
filenames = dircache.listdir( basedir )

for filename in filenames:
    file_path = join( basedir, filename )

    if not isfile(file_path):
        continue
    if isdir(file_path):
        continue

    file_obj = open( file_path, "r" )
    if not file_obj:
        sys.stderr.write( "can't open: %s" % file_path )
        continue

    text_body = file_obj.readline().strip()
    text_body = re.sub( r"^hylom:\s*", "", text_body, 1 )
    if re.search( r"http://", text_body ):
        text_body = re.sub( r"(http://\S+)", r'<a href="\1">\1</a>',text_body )
    text_url = file_obj.readline().strip()
    text_datetime = file_obj.readline().strip()


    # format message
    # if message is reply, skip
    if re.search( r"@[A-Za-z0-9_]*", text_body):
        continue
    
    current_locale = locale.getlocale( locale.LC_TIME )
    locale.setlocale( locale.LC_TIME, "C" )

    # time format: Tue, 13 Jan 2009 09:11:53 +0000
    dt = datetime.strptime( text_datetime, "%a, %d %b %Y %H:%M:%S +0000" )
    # convert UTC to JST
    dt = dt + timedelta( hours=9 )
    timestr = dt.strftime( "%H:%M:%S" )
    output_string = '<li>%s（<a href="%s">%s</a>）</li>' % (text_body, text_url, timestr)
    locale.setlocale( locale.LC_TIME, current_locale )

#    output_string = join(text_body, text_url, text_datetime)
    print "<ul>"
    print output_string
    print "</ul>"
