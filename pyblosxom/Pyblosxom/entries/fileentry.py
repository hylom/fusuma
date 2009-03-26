#######################################################################
# This file is part of PyBlosxom.
#
# Copyright (c) 2003, 2004, 2005, 2006 Wari Wahab
# 
# PyBlosxom is distributed under the MIT license.  See the file LICENSE
# for distribution details.
#
# $Id: fileentry.py,v 1.1.1.1 2008/11/27 17:15:47 hylom Exp $
#######################################################################
"""
This module contains FileEntry class which is used to retrieve entries 
from a file system.  Since pulling data from the file system and parsing 
it is expensive (especially when you have 100s of entries) we delay
fetching data until it's demanded.

The FileEntry calls EntryBase methods addToCache and getFromCache
to handle caching.
"""

__revision__ = "$Revision: 1.1.1.1 $"

import time
import os
import re
from Pyblosxom import tools
from Pyblosxom.entries import base

class FileEntry(base.EntryBase):
    """
    This class gets it's data and metadata from the file specified
    by the filename argument.
    """
    def __init__(self, request, filename, root, datadir=""):
        """
        @param request: the Request object
        @type  request: Request

        @param filename: the complete filename for the file in question
            including path
        @type  filename: string

        @param root: i have no clue what this is
        @type  root: string

        @param datadir: the datadir
        @type  datadir: string
        """
        base.EntryBase.__init__(self, request)
        self._config = request.getConfiguration()
        self._filename = filename.replace(os.sep, '/')
        self._root = root.replace(os.sep, '/')

        self._datadir = datadir or self._config["datadir"]
        if self._datadir.endswith(os.sep):
            self._datadir = self._datadir[:-1]

        self._timetuple = tools.filestat(self._request, self._filename)
        self._mtime = time.mktime(self._timetuple)
        self._fulltime = time.strftime("%Y%m%d%H%M%S", self._timetuple)

        self._populated_data = 0

    def __repr__(self):
        """
        Returns a representation of this instance with the filename
        and root.
        """
        return "<fileentry f'%s' r'%s'>" % (self._filename, self._root)

    def setTimeLazy(self, timetuple):
        """
        Set the time without populating the entry.

        @param timetuple: the mtime of the file (same as returned by 
                          time.localtime(...))   
        @type  timetuple: tuple of 9 ints     
        """
        self._timetuple = timetuple
        self._mtime = time.mktime(timetuple)
        self._fulltime = time.strftime("%Y%m%d%H%M%S", timetuple)

    def getId(self):
        """
        Returns the id for this content item--in this case, it's the
        filename.

        @returns: the id of the fileentry (the filename)
        @rtype: string
        """
        return self._filename

    def getData(self):
        """
        Returns the data for this file entry.  The data is the parsed
        (via the entryparser) content of the entry.  We do this on-demand
        by checking to see if we've gotten it and if we haven't then
        we get it at that point.

        @returns: the content for this entry
        @rtype: string
        """
        if self._populated_data == 0:
            self.__populatedata()
        return self._data

    def getMetadata(self, key, default=None):
        """
        This overrides the L{base.EntryBase} getMetadata method.

        Note: We populate our metadata lazily--only when it's requested.
        This delays parsing of the file as long as we can.

        @param key: the key being sought
        @type  key: varies

        @param default: the default to return if the key does not
            exist
        @type  default: varies

        @return: either the default (if the key did not exist) or the
            value of the key in the metadata dict
        @rtype: varies
        """
        if self._populated_data == 0:
            self.__populatedata()

        return self._metadata.get(key, default)
        
    def __populatedata(self):
        """
        Fills the metadata dict with metadata about the given file.  This
        metadata consists of things we pick up from an os.stat call as
        well as knowledge of the filename and the root directory.
        We then parse the file and fill in the rest of the information
        that we know.
        """
        file_basename = os.path.basename(self._filename)

        path = self._filename.replace(self._root, '')
        path = path.replace(os.path.basename(self._filename), '')
        path = path[:-1]

        absolute_path = self._filename.replace(self._datadir, '')
        absolute_path = self._filename.replace(self._datadir, '', 1)
        absolute_path = absolute_path.replace(file_basename, '')
        absolute_path = absolute_path[1:][:-1]

        if absolute_path and absolute_path[-1] == "/":
            absolute_path = absolute_path[0:-1]

        filenamenoext = os.path.splitext(file_basename)[0]
        if absolute_path == '':
            file_path = filenamenoext
        else:
            file_path = '/'.join((absolute_path, filenamenoext))

        tb_id = '%s/%s' % (absolute_path, filenamenoext)
        tb_id = re.sub(r'[^A-Za-z0-9]', '_', tb_id)

        self['path'] = path
        self['tb_id'] = tb_id
        self['absolute_path'] = absolute_path
        self['file_path'] = file_path
        self['fn'] = filenamenoext
        self['filename'] = self._filename

        # timetuple is set at __init__ time or by setTimeLazy
        self.setTime(self._timetuple)

        data = self._request.getData()

        entrydict = self.getFromCache(self._filename)
        if not entrydict:
            fileext = os.path.splitext(self._filename)
            if fileext:
                fileext = fileext[1][1:]

            eparser = data['extensions'][fileext]
            entrydict = eparser(self._filename, self._request)
            self.addToCache(self._filename, entrydict)

        self.update(entrydict)
        self._populated_data = 1

# vim: tabstop=4 shiftwidth=4
