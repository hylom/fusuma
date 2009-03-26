#!/usr/bin/env python
#######################################################################
# This file is part of Fusuma website management system.
#
# Copyright (c) hylom <hylomm at gmail.com>, 2008.
# 
# This file is released under the GPL.
#
# $Id: SessionMan.py,v 1.1.1.1 2008/11/27 17:15:37 hylom Exp $
#######################################################################
"""
This is Fusuma's session management module.
"""

__revision__ = "$Revision: 1.1.1.1 $"

import cgi
import sys
import os
import random
import md5
import marshal

VERSION = "0.0.1"
VERSION_DATE = VERSION + " 09/26/2008"
VERSION_SPLIT = tuple(VERSION.split('.'))


class Session(object):
    """
    SessionMan's Session object.
    """
    def __init__(self, sid_str, database_dir):
        """
        Initialize Session.

        @param session_id: session ID
        @type session_id: string
        """
        # create session object
        self._session_obj = { "sid":sid_str }

        # store session object
        # TODO: This session-data-file-name-rule may be insecure!
        self._output_file = "%s/%s" % (database_dir, sid_str)
        self._sid_str = sid_str

    def sid(self):
        """
        getter of _sid_str.
        """
        return self._sid_str

    def delete(self):
        """
        delete session.
        """
        if( os.path.exists(self._output_file) ) :
            os.remove( self._output_file )

        #TODO: need session clean system.

    def save(self):
        """
        save session.
        """
        out_fh = open( self._output_file, "wb" )
        marshal.dump( self._session_obj, out_fh )
        out_fh.close()

    def load(self):
        """
        load session.
        """
        if( os.path.exists(self._output_file) ) :
            out_fh = open( self._output_file, "rb" )
            session_obj = marshal.load( out_fh )
            out_fh.close()
            if( session_obj["sid"] == self.sid() ) :
                self._session_obj = session_obj
                return True
            else:
                return False
        else:
            return False

    def value_from_key( self, key ):
        """
        get value associated key.

        @param key: object key
        @type key: string
        """
        return self._session_obj[key]


    def add_object(self, key, object):
        """
        add object to session.

        @param key: object key
        @type key: string

        @param data: object added to session
        @type data: object
        """

        self._session_obj[key] = object
        


class SessionMan(object):
    """
    This is Fusuma's session management class.
    """
    def __init__(self, database_dir=""):
        """
        Initialize Session Manager.

        @param database_dir: database directory
        @type database_dir: string
        """
        self._database_dir = database_dir

    def new_session(self, loginname):
        """
        create new session.

        @param loginname: loginname string
        @type loginname: string
        """

        # generate session ID
        random.seed()
        m = md5.new()
        rand_str = "%s+%.32f" %( loginname , random.random() )
        m.update( rand_str )
        sid_str = "%s-%s" % ( loginname, m.hexdigest() )
        # end of generate session ID

        return Session( sid_str, self._database_dir )

    def get_session_from_id(self, id):
        """
        retrive session object from id string.

        @param id: session id
        @type id: string
        """
        session = Session( id, self._database_dir )
        
        if( session.load() ):
            return session
        else:
            return None
