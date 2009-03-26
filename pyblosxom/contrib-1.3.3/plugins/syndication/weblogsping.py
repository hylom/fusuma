# vim: tabstop=4 shiftwidth=4 expandtab
"""
Pings Weblogs.com and blo.gs with every new entry

Requires a file in the server that is writable by the webserver. (Default file
is py['datadir']/LATEST).

If your py['datadir'] is read only to the web server, you can create a
directory and make sure that it's writable by the webserver, e.g. 'chmod 777
directory' or using some other methods (mine runs pyblosxom in SuExec mode).

After doing so, change the self._file value in __init__() and you're game.

You can read the data of the self._file using cPickle in python interactive
mode to see if your ping is successful:
>>> import cPickle
>>> cPickle.load(open('/path/to/data/file'))


Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished
to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Copyright 2004, 2005 Wari Wahab
"""
__author__ = "Wari Wahab pyblosxom@wari.per.sg"
__version__ = "$Id: weblogsping.py,v 1.1.1.1 2008/11/27 17:15:40 hylom Exp $"

import xmlrpclib, os, sys, time
import cPickle as pickle
from Pyblosxom import tools

class WeblogsPing:
    def __init__(self, request):
        config = request.getConfiguration()
        pyhttp = request.getHttp()
        data = request.getData()

        self._pingData = {}
        entryList = data['entry_list']
        if entryList:
            self._latest = entryList[0]['mtime']
        else:
            self._latest = 0
        self._file = os.path.join(config['datadir'], 'LATEST')
        self._title = config['blog_title']

        # FIXME - do we want to use config["base_url"] instead here?
        self._site = 'http://%s%s' % (pyhttp['HTTP_HOST'], pyhttp['SCRIPT_NAME'])
        self._xml = self._site + '?flav=rss'

    def ping(self):
        if os.path.isfile(self._file):
            try:
                fp = open(self._file, 'rb')
                self._pingData = pickle.load(fp)
                fp.close()
            except IOError:
                # Something wrong with the file, abort.
                return
        else:
            # If we cannot save, forget about pinging
            if not self.__saveResults(0, 'fresh', 'fresh'):
                return
        
        # Timecheck.
        if self._latest > self._pingData['lastPing'] or \
           self._latest > self._pingData['latest']:
            self.__doPing()
        return

    def __doPing(self):
        pingTime = int(time.time())
        # Save this data first else we'll go crazy with looping
        if not self.__saveResults(pingTime, 'buffer', 'buffer'):
            return

        # Ping both servers now.
        logger = tools.getLogger()
        try:
            rpc = xmlrpclib.Server('http://ping.blo.gs/')
            response = rpc.weblogUpdates.extendedPing(
                self._title, self._site, self._xml, self._xml)
            rpc = xmlrpclib.Server('http://rpc.weblogs.com/RPC2')
            response1 = rpc.weblogUpdates.ping(self._title, self._site)

            # save result of ping in self._file, note, no output is done
            self.__saveResults(pingTime, response, response1)
        except:
            logger.error("Error during ping: %s, %s" % (str(sys.exc_type),
                                                        str(sys.exc_value)))
            

    def __saveResults(self, pingTime, response, response1):
        latest = (pingTime == 0 and 1 or self._latest)
        self._pingData = {'lastPing' : pingTime,
                         'response' : response,
                         'response1' : response1,
                         'latest' : latest}
        try:
            fp = open(self._file, 'w+b')
            pickle.dump(self._pingData, fp, 1)
            fp.close()
            return 1
        except IOError:
            # Something wrong with the file, abort.
            return 0

def cb_prepare(args):
    request = args["request"]
    WeblogsPing(request).ping()
