#!/usr/bin/env python
#######################################################################
# This file is part of Fusuma website management system.
#
# Copyright (c) hylom <hylomm at gmail.com>, 2008.
# 
# This file is released under the GPL.
#
# $Id: DataMan.py,v 1.1.1.1 2008/11/27 17:15:36 hylom Exp $
#######################################################################
"""
This is Fusuma's article data management module.
"""

__revision__ = "$Revision: 1.1.1.1 $"

import datetime
import sys
import os


VERSION = "0.0.1"
VERSION_DATE = VERSION + " 09/26/2008"
VERSION_SPLIT = tuple(VERSION.split('.'))


class DataMan(object):
    """
    This is Fusuma's story data management class.
    """
    def __init__(self, document_root):
        """
        Initialize Data Manager.

        @param document_root: document root directory
        @type document_root: string
        """
        self._document_root = document_root

    def new_story(self):
        """
        create new story.
        """
        story = Story()
        story.output_dir = _get_output_path

#        Story.property()[""] = 

    def _get_output_path(self):
        """
        return directory which story is saved.
        
        default is: <document_root>/yyyy/mm/dd/
        """
        dt = datetime.datetime.today();

        current_locale = locale.getlocale( locale.LC_CTYPE )
        locale.setlocale( locale.LC_CTYPE, "" )

        path = dt_expire.strftime( "%Y/%m/%d" )

        locale.setlocale( locale.LC_CTYPE, current_locale )

        return path;
        

class Story:
    """
    DataMan's Story object.
    """
    def __init__(self):
        """
        Initialize Story.
        """

        # store session object
        # TODO: This session-data-file-name-rule may be insecure!
        self._output_file = ""
        self._output_dir = ""
        self._story = ""
        self._property = {}

    def save(self):
        """
        Save story to file.
        """
        

## accessor
    def property(self):
        return self._property

    def output_file(self):
        return self._output_file

    def set_output_file(self, str):
        self._output_file = str

    def output_dir(self):
        return self._output_dir

    def set_output_dir(self, str):
        self._output_dir = str

    def story(self):
        return self._story

    def set_story(self, str):
        self._story = str


