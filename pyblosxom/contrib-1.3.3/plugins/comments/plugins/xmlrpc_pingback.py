"""
This module contains an XML-RPC extension to support pingback
<http://www.hixie.ch/specs/pingback/pingback> pings.   You must have the 
comments plugin installed as well, although you don't need to enable comments 
on your blog in order for trackbacks to work.

You must add a pingback <link> element to your HTML for auto-discovery. For
example, if your site is located at http://foo.com/bar, your header HTML should
contain this in its <meta> section:

  <link rel="pingback" href="http://foo.com/bar/RPC" />

Note that the URL must be absolute. If your xmlrpc_urltrigger config bariable
is set to something other than RPC, modify the <link> element accordingly.

This test blog, maintained by Ian Hickson, is useful for testing. You can post
to it, linking to a post on your site, and it will send a pingback.

  http://www.dummy-blog.org/

Copyright (c) 2003-2006 Ted Leung, Ryan Barrett

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

from config import py
from Pyblosxom.pyblosxom import PyBlosxom
from Pyblosxom import tools
from xmlrpclib import Fault

import os, re, sgmllib, time, urllib, urlparse

def verify_installation(request):
    # no config parameters
    return 1

class parser(sgmllib.SGMLParser):
    """ Shamelessly grabbed from Sam Ruby
    from http://www.intertwingly.net/code/mombo/pingback.py
    """
    """ extract title and hrefs from a web page"""
    intitle=0
    title = ""
    hrefs = []

    def do_a(self, attrs):
        attrs=dict(attrs)
        if attrs.has_key('href'): self.hrefs.append(attrs['href'])
        
    def do_title(self, attrs):
        if self.title=="": self.intitle=1
    def unknown_starttag(self, tag, attrs):
        self.intitle=0
    def unknown_endtag(self,tag):
        self.intitle=0
    def handle_charref(self, ref):
        if self.intitle: self.title = self.title + ("&#%s;" % ref)
    def handle_data(self,text):
        if self.intitle: self.title = self.title + text

def fileFor(req, uri):
    config = req.getConfiguration()
    data = req.getData()
    urldata = urlparse.urlsplit(uri)

    # Reconstruct uri to something sane
    uri = "%s://%s%s" % (urldata[0], urldata[1], urldata[2])
    fragment = urldata[4]

    # We get our path here
    path = uri.replace(config['base_url'], '')
    req.addHttp({'PATH_INFO': path, "form": {}})
    from Pyblosxom.pyblosxom import blosxom_process_path_info
    blosxom_process_path_info({'request': req})
    
    args = { 'request': req }
    from Pyblosxom.pyblosxom import blosxom_file_list_handler
    es = blosxom_file_list_handler(args)

    # We're almost there
    if len(es) == 1 and path.find(es[0]['file_path']) >= 0:
        return es[0]

    # Could be a fragment link
    for i in es:
        if i['fn'] == fragment:
            return i

    # Point of no return
    if len(es) >= 1:
        raise Fault(0x0021, "%s cannot be used as a target" % uri)
    else:
        raise Fault(0x0020, "%s does not exist")

            
def pingback(request, source, target):
    logger = tools.getLogger()
    logger.info("pingback started")
    source_file = urllib.urlopen(source.split('#')[0])
    if source_file.headers.get('error', '') == '404':
        raise Fault(0x0010, "Target %s not exists" % target)
    source_page = parser()
    source_page.feed(source_file.read())
    source_file.close()

    if source_page.title == "": source_page.title = source
    
    if target in source_page.hrefs:
        target_entry = fileFor(request, target)

        body = ''
        try:
            from rssfinder import getFeeds
            from rssparser import parse

            baseurl=source.split("#")[0]
            for feed in getFeeds(baseurl):
                for item in parse(feed)['items']:
                    if item['link']==source:
                        if 'title' in item: source_page.title = item['title']
                        if 'content_encoded' in item: body = item['content_encoded'].strip()
                        if 'description' in item: body = item['description'].strip() or body
                        body=re.compile('<.*?>',re.S).sub('',body)
                        body=re.sub('\s+',' ',body)
                        body=body[:body.rfind(' ',0,250)][:250] + " ...<br />"
        except:
            pass

        cmt = {'title':source_page.title, \
               'author':'Pingback from %s' % source_page.title,
               'pubDate' : str(time.time()), \
               'link': source,
               'source' : '',
               'description' : body}
        
        # run anti-spam plugins
        argdict = { "request": request, "comment": cmt }
        reject = tools.run_callback("trackback_reject",
                                    argdict,
                                    donefunc=lambda x:x != 0)
        if ((isinstance(reject, tuple) or isinstance(reject, list))
            and len(reject) == 2):
            reject_code, reject_message = reject
        else:
            reject_code, reject_message = reject, "Pingback rejected."
        if reject_code == 1:
            raise Fault(0x0031, reject_message)

        from comments import writeComment
        config = request.getConfiguration()
        data = request.getData()
        data['entry_list'] = [ target_entry ]

        # TODO: Check if comment from the URL exists
        writeComment(request, config, data, cmt, config['blog_encoding'])
               
        return "success pinging %s from %s\n" % (target, source)
    else:
        raise Fault(0x0011, "%s does not point to %s" % (source, target))

def cb_xmlrpc_register(args):
    """
    Register as a pyblosxom XML-RPC plugin
    """
    args['methods'].update({'pingback.ping': pingback })
    return args

def cb_start(args):
    request = args["request"]
    config = request.getConfiguration()

    logger = tools.getLogger()
    logger.info("finished config")
