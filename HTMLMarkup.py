#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# HTMLMarkup.py
#

import os, sys, re

def markup_ul(str_line, fo_in, indent_lv=""):
    re_ul = re.compile( r"(\t*)・(.*)$" )
    str_out = indent_lv + "<ul>\n"
    str_out = str_out + indent_lv + "  " + re_ul.sub( r"<li>\2</li>", str_line )

    for str_line in fo_in:
        if not re_ul.search( str_line ):
            str_out = str_out + indent_lv + "</ul>\n\n"
            str_out = str_out + str_line
            break

        next_indent_lv = re_ul.search( str_line ).group(1)

        if len(next_indent_lv) > len(indent_lv):
            str_out = str_out + markup_ul( str_line, fo_in, next_indent_lv )

        elif len(next_indent_lv) < len(indent_lv):
            str_out = next_indent_lv + "</ul>\n\n"
            return str_out

        else:
            str_out = str_out + indent_lv + "  " + re_ul.sub( r"<li>\2</li>", str_line )

    return str_out


re_h4 = re.compile( r"^●(.*)$" )
re_p = re.compile( r"^(　.*)$" )
re_ul = re.compile( r"^・(.*)$" )
fo_in = sys.stdin

for line in fo_in:
    line = re_h4.sub( r"<h4>\1</h4>", line )
    line = re_p.sub( r"<p>\1</p>", line )

    if re_ul.search( line ):
        line = markup_ul(line, fo_in)

    print line,


