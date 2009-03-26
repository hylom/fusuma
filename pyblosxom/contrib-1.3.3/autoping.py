#!/usr/bin/env python
"""Ping all traceback-eligable or pingback-elibable servers associated with 
hrefs found in a given blog entry - Most code is by Sam Ruby

One requirement for this is that you run this code in your py['datadir']. This
script can be placed anywhere. If your entry is placed in,
technology/stuff.txt, run autoping this way.

cd /your/blog/dir
/path/to/autoping.py technology/stuff.txt

Autoping will try to send a trackback and/or pingback based on the URLs it
found on technology/stuff.txt. There's a limitation that, if the autodiscovery
in the trackback RDF in the site does not properly point to the correct URL to
ping, autoping will not be able to send out the trackback. Alert the author of
the site.
"""

# Please change this value to where you pyblosxom is installed.
#BASEURL = 'http://roughingit.subtlehints.net/pyblosxom/'
# Modify this to where your pyblosxom and config.py is installed
import sys
#sys.path.append('/path/to/config')
#sys.path.append('/path/to/Pyblosxom/dir')


import re, sgmllib, sys, urllib, xmlrpclib
from xml.sax import parseString, SAXParseException
from xml.sax.handler import ContentHandler
import cPickle, os, os.path

# Get our pyblosxom specifics here
from Pyblosxom import tools
from Pyblosxom.pyblosxom import blosxom_entry_parser
from Pyblosxom.Request import Request
import config

logdir = config.get("logdir", "/tmp")
logfile = os.path.normpath(logdir + os.sep + "autoping.log")
logger = tools.getLogger()

def excerpt(filename, title, body, blogname):
    """ filename,title,body => url,args

    Excerpt the body and urlencode the trackback arguments.
    """

    body = re.split('<div\s+class="excerpt">(.*?)<\/div>',body)[:2][-1]

    body = re.sub('\n',' ',body)
    body = re.sub('&nbsp;',' ',body)
    body = re.sub('^(<p>)?<a\s+href="\S+">[\w\s\.]+<\/a>:\s*','',body)
    body = re.sub('<em>.*?<\/em>\.?\s*','',body)
    body = re.sub('<.*?>','',body)

    body = body[:252]

    url = BASEURL + filename
    url = re.sub('\.[a-zA-Z]+$','',url)

    arg = {}
    arg['url'] = url
    arg['title'] = title
    arg['blog_name'] = blogname
    arg['excerpt'] = body

    return url, urllib.urlencode(arg)


class link(sgmllib.SGMLParser):
    """ source -> list of trackbacks, list of pingbacks

    Parse a given html page, and retrieve the trackbacks associated with
    pages referenced via href found.
    """

    def __init__(self, name, title, body, blogname):
        sgmllib.SGMLParser.__init__(self)
        self.trackbacks = []
        self.pingbacks  = []
        self.title = title
        (self.url,self.args) = excerpt(name, title, body, blogname)
        self.feed(body)

    def start_a(self, attrs):
        attrs = dict(attrs)
        if attrs.has_key('href'):
            try:
                href = attrs['href']
                trackback,pingback = backrefs(href)
                self.trackbacks = self.trackbacks + trackback
                self.pingbacks  = self.pingbacks  + pingback
            except:
                pass


tb_re=re.compile('(<rdf:RDF .*?</rdf:RDF>)')
pb_re=re.compile('<link rel="pingback" href="([^"]+)" ?/?>')
def backrefs(href):
    """ href -> ([trackbacks],[pingbacks])

    Parse a given html page, and retrieve the rdf:about, X-Pingback header,
    or pingback link information associated with a given href.  At most
    one is returned (in the above priority).
    """

    base = href.split("#")[0]
    file = urllib.urlopen(base)
    info = file.info()
    data = file.read().replace('\n',' ')
    file.close()

    trackback = []
    pingback = pb_re.findall(data)[:1]

    for x in tb_re.findall(data):
        try:
            parseString(x, rdf())
        except SAXParseException:
            pass

    if info.has_key("X-Pingback"): pingback=[info["X-Pingback"]]
    if rdf.ids.has_key(href): trackback = [rdf.ids[href]]
    if not trackback and not pingback and href.find("#")>0:
        if rdf.ids.has_key(base): trackback = [rdf.ids[base]]

    if trackback: pingback=[]
    if pingback:  pingback=[(href, pingback[0])]

    return (trackback, pingback)


class rdf(ContentHandler):
    """ xml -> dictionary of {dc:identifier => trackback:ping|rdf:about}

    Parse a given html page, and retrieve the rdf:about information associated
    with a given href.
    """

    ids = {}
    def startElement(self, name, attrs):
        if name == 'rdf:Description':
            attrs=dict(attrs)
            if attrs.has_key('dc:identifier'):
                if attrs.has_key('trackback:ping'):
                        self.ids[attrs['dc:identifier']] = attrs['trackback:ping']
                elif attrs.has_key('about'):
                        self.ids[attrs['dc:identifier']] = attrs['about']
                elif attrs.has_key('rdf:about'):
                        self.ids[attrs['dc:identifier']] = attrs['rdf:about']

def trackback(parser):
    """ parser -> None

    Ping all trackbacks encountered with the url, title, blog_name, and 
    excerpt.
    """

    for url in parser.trackbacks:
        try:
            logger.info("")
            logger.info("*** Trackback " + url)
            logger.info(parser.args)
            if url.find('?tb_id=') >= 0:
                file=urllib.urlopen(url + "&" + parser.args)
            else:
                file=urllib.urlopen(url, parser.args)
            logger.info(file.read())
            file.close()
        except Exception, e:
            logger.error(e)


def pingback(parser):
    """ parser -> None

    Ping all pingbacks encountered with the source and targets
    """

    for target,server in parser.pingbacks:
        try:
            logger.info("")
            logger.info("*** Pingback " + server)
            server=xmlrpclib.Server(server)
            logger.info(server.pingback.ping(parser.url,target))
        except Exception, e:
            logger.error(e)

def autoping(name):
    request = Request()
    # Load up the cache (You can just import the base cache here)
    cache_driver = tools.importName('Pyblosxom.cache', config.py.get('cacheDriver', 'base'))
    cache = cache_driver.BlosxomCache(request, config.py.get('cacheConfig', ''))
    try:
        filename = os.path.join(config.py['datadir'], name)
        entryData = {}
        cache.load(filename)
        # Look for cached documents
        if cache.isCached():
            entryData = cache.getEntry()
            
        # Cached? Try our entryparsers then.
        if not entryData:
            fileExt = re.search(r'\.([\w]+)$', filename)
            try:
                entryData = blosxom_entry_parser(filename, request)
            except IOError, e:
                logger.error(e)
        
        name = re.sub(config.py['datadir'],'',name)
        parser = link(name, entryData['title'].strip(), entryData['body'].strip(), config.py['blog_title'])
        trackback(parser)
        pingback(parser)
    except Exception, e:
        logger.error(e)
    

if __name__ == '__main__':
    for name in sys.argv[1:]:
        autoping(name)
