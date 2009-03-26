#!/usr/bin/env python
#######################################################################
# This file is part of Fusuma website management system.
#
# Copyright (c) hylom <hylomm at gmail.com>, 2008.
# 
# This file is released under the GPL.
#
# $Id: PasswordMan.py,v 1.1.1.1 2008/11/27 17:15:37 hylom Exp $
#######################################################################
"""
This is Fusuma's account management module.
"""

__revision__ = "$Revision: 1.1.1.1 $"

import cgi
import sys
import os


VERSION = "0.0.1"
VERSION_DATE = VERSION + " 09/26/2008"
VERSION_SPLIT = tuple(VERSION.split('.'))


class PasswordMan(object):
    """
    This is Fusuma's account management class.
    """
    def __init__(self):
        """
        Initialize Password Manager.
        """


    def get_userId(self, username, passwd):
        """
        This is Fusuma's main routine.

        @param username: username string
        @type username: string

        @param passwd: password string
        @type passwd: string
        """

        # root only!
        if (username == "hylom") and (passwd == "stringer"):
            return 1
        else:
            return -1

