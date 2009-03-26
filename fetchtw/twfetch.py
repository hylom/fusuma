#!/usr/bin/env python
#######################################################################
# twfetch.py : twitter fetcher
#
# Copyright (c) hylom <hylomm at gmail.com>, 2008.
# 
# This file is released under the GPL.
#
# $Id: fsm.py,v 1.1.1.1 2008/11/27 17:15:36 hylom Exp $
#######################################################################

import os
import sys
import re
from urllib import urlopen

#url = "http://twitter.com/hylom"
url = "http://twitter.com/statuses/user_timeline/5638772.rss"
doc = urlopen(url)

# TODO: timeout proc.
xml_rss = doc.read()
doc.close()

#file = open( "xml.txt", "w" )
#file.write( xml )
#file.close

#print xml_rss

re_item = re.compile( "<item>(.*?)</item>", re.S );
items = re_item.findall( xml_rss )

for item in items:
    date = ""
    title = ""
    link = ""

    try:
        date = re.search( "<pubDate>(.*)</pubDate>", item, re.S ).group(1)
        title = re.search( "<title>(.*)</title>", item, re.S ).group(1)
        link = re.search( "<link>(.*)</link>", item, re.S ).group(1)
    except AttributeError:
        None

    print "%s : %s (%s)\n" % (date,title,link)
