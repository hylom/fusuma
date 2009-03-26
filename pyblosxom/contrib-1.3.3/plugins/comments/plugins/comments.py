"""
This module contains an extension to Blosxom file entries to support
comments.

Copyright 2003-2007 by contributors:
  Ted Leung
  Will Guaraldi
  Wari Wahab
  Robert Wall
  Bill Mill
  Roberto De Almeida
  David Geller
  David Pashley
  Ryan Barrett

If you make any changes to this plugin, please a send a patch with your
changes to pyblosxom-devel@sourceforge.net so that we can incorporate your
changes. Thanks!

This module supports the following config parameters (they are not
required):

   comment_dir - the directory we're going to store all our comments in.
                 this defaults to datadir + "comments".
   comment_ext - the file extension used to denote a comment file.
                 this defaults to "cmt".
   comment_draft_ext - the file extension used for new comments that have
                       not been manually approved by you.  this defaults
                       to comment_ext (i.e. there is no draft stage)

   comment_smtp_server - the smtp server to send comments notifications
                         through.
   comment_mta_cmd - alternatively, a command line to invoke your MTA (e.g.
                     sendmail) to send comment notifications through.
   comment_smtp_from - the person comment notifications will be from. If
                        you're using SMTP, this should be an email address
                        accepted by your SMTP server. If you omit this, the
                        from address will be the e-mail address as input in
                        the comment form.
   comment_smtp_to - the person to send comment notifications to.
   comment_nofollow - set this to 1 to add rel="nofollow" attributes to
                 links in the description -- these attributes are embedded
                 in the stored representation.

Comments are stored 1 per file in a parallel hierarchy to the datadir
hierarchy.  The filename of the comment is the filename of the blog
entry, plus the creation time of the comment as a float, plus the 
comment extension.

Comments now follow the blog_encoding variable specified in config.py .
If you don't include a blog_encoding variable, this will default to
iso-8859-1.

Comments will be shown for a given page if one of the following is
true:

 1. the page has only one blog entry on it and the request is for a
    specific blog entry as opposed to a category with only one entry
    in it

 2. if "showcomments=yes" is in the querystring then comments will
    be shown


IMPLEMENTING COMMENT PREVIEW
============================

If you would like comment previews, you need to do 2 things.

 1) Add a preview button to comment-form.html like this:
    <input name="preview" type="submit" value="Preview" />

    You may change the contents of the value attribute, but the name of
    the input must be "preview".

 2) Still in your comment-form.html template, you need to use the comment
    values to fill in the values of your input fields like so:
    <input name="author" type="text" value="$cmt_author">
    <input name="email" type="text" value="$cmt_email">
    <input name="url" type="text" value="$cmt_link">
    <textarea name="body">$cmt_description</textarea>

    If there is no preview available, these variables will be stripped
    from the text and cause no problem.

 3) Copy comment.html to a template called comment-preview.html. All of
    the available variables from the comment template are available for
    this template.


AJAX SUPPORT
============

Comment previewing and posting can optionally use AJAX, as opposed to full
HTTP POST requests. This avoids a full-size roundtrip and re-render, so
commenting feels faster and more lightweight.

AJAX commenting degrades gracefully in older browsers. If JavaScript is
disabled or not supported in the user's browser, or if it doesn't support
XmlHttpRequest, comment posting and preview will use normal HTTP POST.

AJAX comment support requires a few elements in the comment-form flavour
template. These elements are included in default comment-form.html template
that comes with this plugin.

Specifically, the comment-anchor tag must be the first thing in the template:

  <p id="comment-anchor" />

Also, the form needs some JavaScript. Add an onsubmit handler to the form tag:

<form method="post" action="$base_url/$file_path#comment-anchor"
      name="comments_form" id="comments_form" onsubmit="return false;">

If you run pyblosxom inside cgiwrap, you'll probably need to remove
#comment-anchor from the URL in the action attribute. They're incompatible.
(Your host may even be using cgiwrap without your knowledge. If AJAX comment
previewing and posting don't work, try removing #comment-anchor.)

Next, add onclick handlers to the button input tags:

<input value="Preview" name="preview" type="button" id="preview"
       onclick="send_comment('preview');" />
<input value="Submit" name="submit" type="button" id="post"
       onclick="send_comment('post');" />

Finally, include this script tag somewhere after the </form> closing tag:

  <script type="text/javascript" src="/comments.js"></script>

(Note the separate closing </script> tag! It's for IE; without it, IE won't
actually run the code in comments.js.)


NOFOLLOW SUPPORT
================

This plugin implements Google's nofollow support for links in the body of the 
comment. If you display the link of the comment poster in your HTML template 
then you must add the rel="nofollow" attribute to your template as well


NOTE TO DEVELOPERS WHO ARE WRITING PLUGINS THAT CREATE COMMENTS
===============================================================

Each entry has to have the following properties in order to work with
comments:

 1. absolute_path - the category of the entry.  
    ex. "dev/pyblosxom"
 2. fn - the filename of the entry without the file extension and without
    the directory.  
    ex. "staticrendering"
 3. file_path - the absolute_path plus the fn.  
    ex. "dev/pyblosxom/staticrendering"

Also, if you don't want comments for an entry, add "nocomments" = 1
to the properties for the entry.


WHERE TO FIND ADDITIONAL MATERIAL
=================================

There is a README file that comes with the contributed plugins pack
in contrib/plugins/comments/ which has more information on installing
the comments plugin.

Additionally, there is a chapter in the PyBlosxom manual that
covers installing and configuring the comments plugin.  The manual
is on the PyBlosxom web-site: http://pyblosxom.sourceforge.net/

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
__author__ = "Ted Leung"
__version__ = "$Id: comments.py,v 1.1.1.1 2008/11/27 17:15:40 hylom Exp $"
__url__ = "http://pyblosxom.sourceforge.net/"
__description__ = "Allows for comments on each blog entry."

import cgi, glob, os.path, re, time, cPickle, os, codecs, sys, popen2, \
  traceback, types
from email.MIMEText import MIMEText
from xml.sax.saxutils import escape
from Pyblosxom import tools
from Pyblosxom.entries.base import EntryBase
from Pyblosxom.renderers import blosxom

def cb_start(args):
    request = args["request"]
    config = request.getConfiguration()

    if not config.has_key('comment_dir'):
        config['comment_dir'] = os.path.join(config['datadir'],'comments')
    if not config.has_key('comment_ext'):
        config['comment_ext'] = 'cmt'
    if not config.has_key('comment_draft_ext'):
        config['comment_draft_ext'] = config['comment_ext']
    if not config.has_key('comment_nofollow'):
        config['comment_nofollow'] = 0
    
def verify_installation(request):
    config = request.getConfiguration()

    retval = 1

    if config.has_key('comment_dir') and not os.path.isdir(config['comment_dir']):
        print 'The "comment_dir" property in the config file must refer to a directory'
        retval = 0

    smtp_keys_defined = []
    smtp_keys=['comment_smtp_server', 'comment_smtp_from', 'comment_smtp_to']
    for k in smtp_keys:
        if config.has_key(k):
            smtp_keys_defined.append(k)

    if smtp_keys_defined:
        for i in smtp_keys:
            if i not in smtp_keys_defined:
                print("Missing comment SMTP property: '%s'" % i)
                retval = 0
    
    optional_keys = ['comment_dir', 'comment_ext', 'comment_draft_ext']
    for i in optional_keys:
        if not config.has_key(i):
            print("missing optional property: '%s'" % i)

    return retval

def createhtmlmail (html, headers):
    """
    Create a mime-message that will render HTML in popular
    MUAs, text in better ones

    Based on: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/67083
    """
    import MimeWriter
    import mimetools
    import cStringIO
    
    out = cStringIO.StringIO() # output buffer for our message 
    htmlin = cStringIO.StringIO(html)

    text = re.sub('<.*?>', '', html)
    txtin = cStringIO.StringIO(text)
    
    writer = MimeWriter.MimeWriter(out)
    for header,value in headers:
        writer.addheader(header, value)
    writer.addheader("MIME-Version", "1.0")
    writer.startmultipartbody("alternative")
    writer.flushheaders()

    subpart = writer.nextpart()
    subpart.addheader("Content-Transfer-Encoding", "quoted-printable")
    pout = subpart.startbody("text/plain", [("charset", 'us-ascii')])
    mimetools.encode(txtin, pout, 'quoted-printable')
    txtin.close()

    subpart = writer.nextpart()
    subpart.addheader("Content-Transfer-Encoding", "quoted-printable")
    pout = subpart.startbody("text/html", [("charset", 'us-ascii')])
    mimetools.encode(htmlin, pout, 'quoted-printable')
    htmlin.close()

    writer.lastpart()
    msg = out.getvalue()
    out.close()

    return msg

def readComments(entry, config):
    """
    @param: a file entry
    @type: dict
    
    @returns: a list of comment dicts
    """
    encoding = config['blog_encoding']
    filelist = glob.glob(cmtExpr(entry, config))
    if not entry.has_key('num_comments'):
        entry['num_comments'] = len(filelist)
    comments = [readComment(f, encoding, config) for f in filelist]
    comments = [(cmt['cmt_time'], cmt) for cmt in comments]
    comments.sort()
    return [c[1] for c in comments]
    
def getCommentCount(entry, config):
    """
    @param: a file entry
    @type: dict
    
    @returns: the number of comments for the entry
    """
    if entry['absolute_path'] == None: return 0
    filelist = glob.glob(cmtExpr(entry,config))
    if filelist is not None:
        return len(filelist)
    return 0

def cmtExpr(entry, config):
    """
    Return a string containing the regular expression for comment entries
    
    @param: a file entry
    @type: dict
    @returns: a string with the directory path for the comment
    
    @param: configuratioin dictionary
    @type: dict
    
    @returns: a string containing the regular expression for comment entries
    """
    cmtDir = os.path.join(config['comment_dir'], entry['absolute_path'])
    cmtExpr = os.path.join(cmtDir,entry['fn']+'-*.'+config['comment_ext'])
    return cmtExpr

def readComment(filename, encoding, config):
    """
    Read a comment from filename
    
    @param filename: filename containing a comment
    @type filename: string

    @param encoding: encoding of comment files
    @type encoding: string
    
    @param config: the pyblosxom configuration settings
    @type config: dictionary
    
    @returns: a comment dict
    """
    from xml.sax import make_parser, SAXException
    from xml.sax.handler import feature_namespaces, ContentHandler
    class cmtHandler(ContentHandler):
        def __init__(self, cmt):
            self._data = ""
            self.cmt = cmt
        def startElement(self, name, atts):
            self._data = ""
        def endElement(self, name):
            self.cmt['cmt_'+name] = self._data
        def characters(self, content):
            self._data += content

    cmt = {}
    
    try:
        parser = make_parser()
        parser.setFeature(feature_namespaces, 0)
        handler = cmtHandler(cmt)
        parser.setContentHandler(handler)
        parser.parse(filename)
        cmt['cmt_time'] = float(cmt['cmt_pubDate'])                #time.time()
        cmt['cmt_pubDate'] = time.ctime(float(cmt['cmt_pubDate'])) #pretty time
        cmt['cmt_w3cdate'] = time.strftime('%Y-%m-%dT%H:%M:%SZ',
                                           time.gmtime(cmt['cmt_time']))
        if cmt['cmt_link']:
            link = add_dont_follow('<a href="%s">%s</a>' % (cmt['cmt_link'],
                                                            cmt['cmt_author']),
                                   config)
            cmt['cmt_optionally_linked_author'] = link
        else:
            cmt['cmt_optionally_linked_author'] = cmt['cmt_author']
        return cmt
    except: #don't error out on a bad comment
        logger = tools.getLogger()
        logger.error("bad comment file: %s\nerror was: %s" %
                     (filename, traceback.format_exception(*sys.exc_info())))

def writeComment(request, config, data, comment, encoding):
    """
    Write a comment
    
    @param config: dict containing pyblosxom config info
    @type  config: dict
    
    @param data: dict containing entry info
    @type  data: dict
    
    @param comment: dict containing comment info
    @type  comment: dict

    @return: The success or failure of creating the comment.
    @rtype: string
    """
    entry_list = data.get("entry_list", [])
    if not entry_list:
        return "No such entry exists."

    entry = data['entry_list'][0]
    cdir = os.path.join(config['comment_dir'],entry['absolute_path'])
    cdir = os.path.normpath(cdir)
    if not os.path.isdir(cdir):
        os.makedirs(cdir)

    cfn = os.path.join(cdir,entry['fn']+"-"+comment['pubDate']+"."+config['comment_draft_ext'])

    def makeXMLField(name, field):
        return "<"+name+">" + cgi.escape(field.get(name, "")) + "</"+name+">\n";

    filedata = '<?xml version="1.0" encoding="%s"?>\n' % encoding
    filedata += "<item>\n"
    filedata += makeXMLField('title', comment)
    filedata += makeXMLField('ipaddress', comment)
    filedata += makeXMLField('author', comment)
    filedata += makeXMLField('link', comment)
    filedata += makeXMLField('email', comment)
    filedata += makeXMLField('source', comment)
    filedata += makeXMLField('pubDate', comment)
    filedata += makeXMLField('description', comment)
    filedata += "</item>\n"

    try :
        cfile = codecs.open(cfn, "w", encoding)
    except IOError:
        logger = tools.getLogger()
        logger.error("couldn't open comment file '%s' for writing" % cfn)
        return "Internal error: Your comment could not be saved."
 
    cfile.write(filedata)
    cfile.close()
 
    #write latest pickle
    latest = None
    latestFilename = os.path.join(config['comment_dir'],'LATEST.cmt')
    try:
        latest = open(latestFilename,"w")
    except IOError:
        logger = tools.getLogger()
        logger.error("couldn't open latest comment pickle for writing")
        return "Couldn't open latest comment pickle for writing."
    else:
        modTime = float(comment['pubDate'])

    try:
        cPickle.dump(modTime, latest)
        latest.close()
    except IOError:
        if latest:
            latest.close()

        logger = tools.getLogger()
        logger.error("comment may not have been saved to pickle file.")
        return "Internal error: Your comment may not have been saved."

    if ((config.has_key('comment_mta_cmd') or
         config.has_key('comment_smtp_server')) and
        config.has_key('comment_smtp_to')):
        # FIXME - removed grabbing send_email's return error message
        # so there's no way to know if email is getting sent or not.
        send_email(config, entry, comment, cdir, cfn)

    # figure out if the comment was submitted as a draft
    if config["comment_ext"] != config["comment_draft_ext"]:
       return "Comment was submitted for approval.  Thanks!"

    return "Comment submitted.  Thanks!"

def send_email(config, entry, comment, comment_dir, comment_filename):
    """Send an email to the blog owner on a new comment

    @param config: configuration as parsed by Pyblosxom
    @type config: dictionary

    @param entry: a file entry
    @type config: dictionary

    @param comment: comment as generated by readComment
    @type comment: dictionary

    @param comment_dir: the comment directory
    @type comment_dir: string

    @param comment_filename: file name of current comment
    @type comment_filename: string
    """
    import smtplib
    # import the formatdate function which is in a different
    # place in Python 2.3 and up.
    try:
        from email.Utils import formatdate
    except ImportError:
        from rfc822 import formatdate
    from socket import gethostbyaddr

    author = escape_SMTP_commands(clean_author(comment['author']))
    description = escape_SMTP_commands(comment['description'])
    ipaddress = escape_SMTP_commands(comment.get('ipaddress', '?'))

    if comment.has_key('email'):
        email = escape_SMTP_commands(clean_author(comment['email']))
    else:
        email = config['comment_smtp_from']

    try:
        curl = config['base_url']+'/'+entry['file_path_urlencoded']
        comment_dir = os.path.join(config['comment_dir'], entry['absolute_path'])

        # create the message
        message = []
        message.append("Name: %s" % author)
        if comment.has_key('email'):
            message.append("Email: %s" % comment['email'])
        if comment.has_key('link'):
            message.append("URL: %s" % comment['link'])
        try:
            host_name = gethostbyaddr(ipaddress)[0]
            message.append("Hostname: %s (%s)" % (host_name, ipaddress))
        except:
            message.append("IP: %s" % ipaddress)
        message.append("Entry URL: %s" % curl)
        message.append("Comment location: %s" % comment_filename)
        message.append("\n\n%s" % description)
 
        if (config.has_key('comment_mta_cmd')):
            # set the message headers
            message.insert(0, "")
            message.insert(0, "Subject: comment on %s" % curl)
            message.insert(0, "Date: %s" % formatdate(float(comment['pubDate'])))
            message.insert(0, "To: %s" % config["comment_smtp_to"])
            message.insert(0, "From: %s" % email)

            body = '\n'.join(message).encode('utf-8')

            argv = [config['comment_mta_cmd'],
                    '-s',
                    'comment on %s' % curl,
                    config['comment_smtp_to']]
            # TODO: switch to subprocess when we can require python 2.4
            process = popen2.Popen3(argv, capturestderr=True)
            process.tochild.write(body)
            process.tochild.close()
            process.wait()
            stdout = process.fromchild.read()
            stderr = process.childerr.read()
            tools.getLogger().debug('Ran MTA command: ' + ' '.join(argv))
            tools.getLogger().debug('Received stdout: ' + stdout)
            tools.getLogger().debug('Received stderr: ' + stderr)
            assert stderr == ''  # the except clause below will catch this

        else:
            assert config.has_key('comment_smtp_server')
            server = smtplib.SMTP(config['comment_smtp_server'])
            mimemsg = MIMEText("\n".join(message).encode("utf-8"), 'plain', 'utf-8')

            # set the message headers
            mimemsg["From"] = config["comment_smtp_to"]
            mimemsg["To"] = config["comment_smtp_to"]
            mimemsg["Date"] = formatdate(float(comment["pubDate"]))
            mimemsg["Subject"] = ("comment on %s" % curl)

            # send the message via smtp
            server.sendmail(from_addr=email,
                            to_addrs=config['comment_smtp_to'], 
                            msg=mimemsg.as_string())
            server.quit()

    except Exception, e:
        tools.getLogger().error("error sending email: %s" %
                                traceback.format_exception(*sys.exc_info()))

def clean_author(s):
    """
    Guard against blasterattacko style attacks that embedd SMTP commands in
    author field.

    If author field is more than one line, reduce to one line

    @param the string to be checked
    @type string

    @returns the sanitized string
    """
    return s.splitlines()[0]

def escape_SMTP_commands(s):
    """
    Guard against blasterattacko style attacks that embed SMTP commands by
    using an HTML span to make the command syntactically invalid to SMTP but
    renderable by HTML

    @param the string to be checked
    @type string

    @returns the sanitized string
    """
    def repl_fn(mo):
        return '<span>'+mo.group(0)+'</span>'
    s = re.sub('([Tt]o:.*)',repl_fn,s)
    s = re.sub('([Ff]rom:.*)',repl_fn,s)
    s = re.sub('([Ss]ubject:.*)',repl_fn,s)
    return s

def sanitize(body):
    """
    This code shamelessly lifted from Sam Ruby's mombo/post.py
    """
    body=re.sub(r'\s+$','',body)
    body=re.sub('\r\n?','\n', body)

    # naked urls become hypertext links
    body=re.sub('(^|[\\s.:;?\\-\\]<])' + 
                '(http://[-\\w;/?:@&=+$.!~*\'()%,#]+[\\w/])' +
                '(?=$|[\\s.:;?\\-\\[\\]>])',
                '\\1<a href="\\2">\\2</a>',body)

    # html characters used in text become escaped
    body=escape(body)

    # passthru <a href>, <em>, <i>, <b>, <blockquote>, <br/>, <p>, 
    # <abbr>, <acronym>, <big>, <cite>, <code>, <dfn>, <kbd>, <pre>, <small>
    # <strong>, <sub>, <sup>, <tt>, <var>
    body=re.sub('&lt;a href="([^"]*)"&gt;([^&]*)&lt;/a&gt;',
                '<a href="\\1">\\2</a>', body)
    body=re.sub('&lt;a href=\'([^\']*)\'&gt;([^&]*)&lt;/a&gt;',
                '<a href="\\1">\\2</a>', body)
    body=re.sub('&lt;em&gt;([^&]*)&lt;/em&gt;', '<em>\\1</em>', body)
    body=re.sub('&lt;i&gt;([^&]*)&lt;/i&gt;', '<i>\\1</i>', body)
    body=re.sub('&lt;b&gt;([^&]*)&lt;/b&gt;', '<b>\\1</b>', body)
    body=re.sub('&lt;blockquote&gt;([^&]*)&lt;/blockquote&gt;', 
                '<blockquote>\\1</blockquote>', body)
    body=re.sub('&lt;br\s*/?&gt;\n?','\n',body)

    body=re.sub('&lt;abbr&gt;([^&]*)&lt;/abbr&gt;', '<abbr>\\1</abbr>', body)
    body=re.sub('&lt;acronym&gt;([^&]*)&lt;/acronym&gt;', '<acronym>\\1</acronym>', body)
    body=re.sub('&lt;big&gt;([^&]*)&lt;/big&gt;', '<big>\\1</big>', body)
    body=re.sub('&lt;cite&gt;([^&]*)&lt;/cite&gt;', '<cite>\\1</cite>', body)
    body=re.sub('&lt;code&gt;([^&]*)&lt;/code&gt;', '<code>\\1</code>', body)
    body=re.sub('&lt;dfn&gt;([^&]*)&lt;/dfn&gt;', '<dfn>\\1</dfn>', body)
    body=re.sub('&lt;kbd&gt;([^&]*)&lt;/kbd&gt;', '<kbd>\\1</kbd>', body)
    body=re.sub('&lt;pre&gt;([^&]*)&lt;/pre&gt;', '<pre>\\1</pre>', body)
    body=re.sub('&lt;small&gt;([^&]*)&lt;/small&gt;', '<small>\\1</small>', body)
    body=re.sub('&lt;strong&gt;([^&]*)&lt;/strong&gt;', '<strong>\\1</strong>', body)
    body=re.sub('&lt;sub&gt;([^&]*)&lt;/sub&gt;', '<sub>\\1</sub>', body)
    body=re.sub('&lt;sup&gt;([^&]*)&lt;/sup&gt;', '<sup>\\1</sup>', body)
    body=re.sub('&lt;tt&gt;([^&]*)&lt;/tt&gt;', '<tt>\\1</tt>', body)
    body=re.sub('&lt;var&gt;([^&]*)&lt;/var&gt;', '<var>\\1</var>', body)

    body=re.sub('&lt;/?p&gt;','\n\n',body).strip()

    # wiki like support: _em_, *b*, [url title]
    body=re.sub(r'\b_(\w.*?)_\b', r'<em>\1</em>', body)
    body=re.sub(r'\*(\w.*?)\*', r'<b>\1</b>', body)
    body=re.sub(r'\[(\w+:\S+\.gif) (.*?)\]', r'<img src="\1" alt="\2" />', body)
    body=re.sub(r'\[(\w+:\S+\.jpg) (.*?)\]', r'<img src="\1" alt="\2" />', body)
    body=re.sub(r'\[(\w+:\S+\.png) (.*?)\]', r'<img src="\1" alt="\2" />', body)
    body=re.sub(r'\[(\w+:\S+) (.*?)\]', r'<a href="\1">\2</a>', body).strip()

    # unordered lists: consecutive lines starting with spaces and an asterisk
    chunk=re.compile(r'^( *\*.*(?:\n *\*.*)+)',re.M).split(body)
    for i in range(1, len(chunk), 2):
        (html,stack)=('', [''])
        for indent,line in re.findall(r'( +)\* +(.*)', chunk[i]) + [('','')]:
            if indent>stack[-1]: (stack,html)=(stack+[indent],html+'<ul>\r')
            while indent<stack[-1]: (stack,html)=(stack[:-1],html+'</ul>\r')
            if line: html += '<li>'+line+'</li>\r'
            chunk[i]=html

    # white space
    chunk=re.split('\n\n+', ''.join(chunk))
#    if len(chunk)>1: body='<p>' + '</p>\r<p>'.join(chunk) + '</p>\r'
    body=re.sub('\n','<br />\n', body)
    body=re.compile('<p>(<ul>.*?</ul>)\r</p>?',re.M).sub(r'\1',body)
    body=re.compile('<p>(<blockquote>.*?</blockquote>)</p>?',re.M).sub(r'\1',body)
    body=re.sub('\r', '\n', body)
    body=re.sub('  +', '&nbsp; ', body)

    return body        
        
def dont_follow(mo):
    return '<a rel="nofollow" '+mo.group(1)+'>'

def add_dont_follow(s, config):
    url_pat_str = '<a ([^>]+)>'
    url_pat = re.compile(url_pat_str)
    if config['comment_nofollow'] == 1:
        return url_pat.sub(dont_follow, s)
    else:
        return s

def cb_prepare(args):
    """
    Handle comment related HTTP POST's.
    
    @param request: pyblosxom request object
    @type request: a Pyblosxom request object
    """
    request = args["request"]
    form = request.getHttp()['form']
    config = request.getConfiguration()
    data = request.getData()
    pyhttp = request.getHttp()

    # first we check to see if we're going to print out comments

    # the default is not to show comments
    data['display_comment_default'] = 0        

    # check to see if they have "showcomments=yes" in the querystring
    qstr = pyhttp.get('QUERY_STRING', None)
    if qstr != None:
        parsed_qs = cgi.parse_qs(qstr)
        if parsed_qs.has_key('showcomments'):
            if parsed_qs['showcomments'][0] == 'yes':
                data['display_comment_default'] = 1

    # check to see if the bl_type is "file"
    if data.has_key("bl_type") and data["bl_type"] == "file":
        data["bl_type_file"] = "yes"
        data['display_comment_default'] = 1
 
    # second, we check to see if they're posting a comment and we
    # need to write the comment to disk.
    posting = ((form.has_key('ajax') and form['ajax'].value == 'post') or
               not form.has_key("preview"))
    if (form.has_key("title") and form.has_key("author") and
        form.has_key("body") and posting):

        encoding = config.get('blog_encoding', 'iso-8859-1')
        decode_form(form, encoding)

        body = form['body'].value
        author = form['author'].value
        url = (form.has_key('url') and [form['url'].value] or [''])[0]

        # sanitize incoming data
        body = sanitize(body)
        author = sanitize(author)

        # it doesn't make sense to add nofollow to link here, but we should
        # escape it. If you don't like the link escaping, I'm not attached 
        # to it.
        cmt_time = time.time()
        w3cdate = time.strftime('%Y-%m-%dT%H:%M:%SZ', (time.gmtime(cmt_time)))
        cdict = {'title': form['title'].value,
                 'author' : author,
                 'pubDate' : str(cmt_time),
                 'w3cdate': w3cdate,
                 'link' : massage_link(url),
                 'source' : '',
                 'description' : add_dont_follow(body, config) }

        keys = form.keys()
        keys = [k for k in keys if k not in ["title", "url", "author", "body"]]
        for k in keys:
            cdict[k] = form[k].value

        if form.has_key('email'):
            cdict['email'] = form['email'].value

        cdict['ipaddress'] = pyhttp.get('REMOTE_ADDR', '')

        # record the comment's timestamp, so we can extract it and send it
        # back alone, without the rest of the page, if the request was ajax.
        data['cmt_time'] = float(cdict['pubDate'])

        argdict = { "request": request, "comment": cdict }
        reject = tools.run_callback("comment_reject",
                                    argdict,
                                    donefunc=lambda x:x != 0)
        if ((isinstance(reject, tuple) or isinstance(reject, list)) and
            len(reject) == 2):
            reject_code, reject_message = reject
        else:
            reject_code, reject_message = reject, "Comment rejected."
        if reject_code == 1:
            data["comment_message"] = reject_message
        else:
            data["comment_message"] = writeComment(request, config, data, \
                                                   cdict, encoding)

class AjaxRenderer(blosxom.Renderer):
    """ The renderer used when responding to AJAX requests to preview and post
    comments. Renders *only* the comment and comment-preview divs.
    """
    def __init__(self, request, data):
        out = request.getConfiguration().get('stdoutput', sys.stdout)
        blosxom.Renderer.__init__(self, request, out)
        self._ajax_type = request.getHttp()['form']['ajax'].value
        self._data = data

    def __shouldOutput(self, entry, template_name):
        """ Return whether we should output this template, depending on the
        type of ajax request we're responding to.
        """
        if self._ajax_type == 'preview' and template_name == 'comment-preview':
            return True
        elif (self._ajax_type == 'post' and template_name == 'comment' and
              self._data.get('cmt_time', None) == entry['cmt_time']):
            return True
        else:
            return False

    def outputTemplate(self, output, entry, template_name, override=0):
        if self.__shouldOutput(entry, template_name):
            blosxom.Renderer.outputTemplate(self, output, entry,
                                            template_name, override)

    def _outputFlavour(self, entry, template_name):
        if self.__shouldOutput(entry, template_name):
            blosxom.Renderer._outputFlavour(self, entry, template_name)

def cb_renderer(args):
    request = args['request']
    config = request.getConfiguration()
    http = request.getHttp()
    form = http['form']

    # intercept ajax requests with our renderer
    if (form.has_key('ajax') and http.get('REQUEST_METHOD', '') == 'POST'):
        data = '&'.join(['%s=%s' % (arg.name, arg.value) for arg in form.list])
        tools.getLogger().info('AJAX request: %s' % data)
        return AjaxRenderer(request, request.getData())

def cb_handle(args):
    request = args['request']
    config = request.getConfiguration()

    # serve /comments.js for ajax comments
    if (request.getHttp()['PATH_INFO'] == '/comments.js'):
        response = request.getResponse()
        response.addHeader('Content-Type', 'text/javascript')

        # look for it in each of the plugin_dirs
        for dir in config['plugin_dirs']:
            comments_js = os.path.join(dir, 'comments.js')
            if os.path.isfile(comments_js):
                f = file(comments_js, 'r')
                response.write(f.read())
                f.close()
                return True

def massage_link(linkstring):
    """Don't allow html in the link string. Prepend http:// if there isn't
    already a protocol."""
    for c in "<>'\"":
        linkstring = linkstring.replace(c, '')
    if linkstring and linkstring.find('://') == -1:
        linkstring = 'http://' + linkstring
    return linkstring

def decode_form(d, blog_encoding):
    """Attempt to decode the POST data with a few likely character encodings.

    If the Content-type header in the HTTP request includes a charset, try
    that first. Then, try the encoding specified in the pybloscom config file.
    if Those fail, try iso-8859-1, utf-8, and ascii."""
    encodings = [blog_encoding, 'iso-8859-1', 'utf-8', 'ascii']
    charset = get_content_type_charset()
    if charset:
      encodings = [charset] + encodings

    for key in d.keys():
        for e in encodings:
            try:
                d[key].value = d[key].value.decode(e)
                break
            except:
                continue

def get_content_type_charset():
    """Extract and return the charset part of the HTTP Content-Type header.

    Returns None if the Content-Type header doesn't specify a charset.
    """
    content_type = os.environ.get('CONTENT_TYPE', '')
    match = re.match('.+; charset=([^;]+)', content_type)
    if match:
        return match.group(1)
    else:
      return None

def cb_head(args):
    renderer = args['renderer']
    template = args['template']

    newtemplate = renderer.flavour.get('comment-head','')
    if not newtemplate == '' and len(renderer.getContent()) == 1:
        args['template'] = newtemplate

        # expand all of entry vars for expansion
        entry = args['entry']
        single_entry = entry['entry_list'][0]
        single_entry['title'] # force lazy evaluation
        entry.update(single_entry)
        args['entry'] = entry
    return template
        
def cb_story(args):
    renderer = args['renderer']
    entry = args['entry']
    template = args['template']
    request = args["request"]
    data = request.getData()
    config = request.getConfiguration()
    if len(renderer.getContent()) == 1 \
            and renderer.flavour.has_key('comment-story') \
            and not entry.has_key("nocomments") \
            and data['display_comment_default'] == 1:
        template = renderer.flavour.get('comment-story','')
        args['template'] = args['template'] + template

    entry['num_comments'] = getCommentCount(entry, config)
    return template

def build_preview_comment(form, entry, config):
    """Build a prevew comment by brute force

    @param form: cgi form object (or compatible)
    @type form: Dictionary of objects with a .value propery

    @param entry: pyblosxom entry object
    @type entry: pyblosxom entry object

    @param config: the pyblosxom configuration settings
    @type config: dictionary

    @return: the comment HTML, a string
    """
    c = {}
    # required fields
    try:
        c['cmt_time'] = str(time.time())
        c['cmt_author'] = form['author'].value
        c['cmt_title'] = form['title'].value
        c['cmt_item'] = sanitize(form['body'].value)
        cmt_time = time.time()
        c['cmt_pubDate'] = time.ctime(cmt_time)
        c['cmt_w3cdate'] = time.strftime('%Y-%m-%dT%H:%M:%SZ',
                                         (time.gmtime(cmt_time)))
        c['cmt_description'] = sanitize(form['body'].value)
        c['cmt_description_escaped'] = escape(sanitize(form['body'].value))

        # optional fields
        c['cmt_optionally_linked_author'] = c['cmt_author']
        if form.has_key('url'):
            c['cmt_link'] = massage_link(form['url'].value)
            if c['cmt_link']:
                link = add_dont_follow('<a href="%s">%s</a>' %
                                       (c['cmt_link'], c['cmt_author']),
                                       config)
                c['cmt_optionally_linked_author'] = link

        if form.has_key('email'):
            c['cmt_email'] = form['email'].value

    except KeyError, e:
        c['cmt_error'] = 'Missing value: %s' % e

    entry.update(c)
    return c

def cb_story_end(args):
    renderer = args['renderer']
    entry = args['entry']
    template = args['template']
    request = args["request"]
    data = request.getData()
    form = request.getHttp()['form']
    config = request.getConfiguration()
    if len(renderer.getContent()) == 1 \
            and renderer.flavour.has_key('comment-story') \
            and not entry.has_key("nocomments") \
            and data['display_comment_default'] == 1:
        output = []
        entry['comments'] = readComments(entry, config)
        if entry.has_key('comments'):        
            comment_entry = dict(entry)
            del comment_entry['comments']
            for key in entry.keys():
                if isinstance(entry[key], types.StringTypes):
                    comment_entry[key + '_escaped'] = entry[key + '_escaped']
                    comment_entry[key + '_urlencoded'] = entry[key + '_urlencoded']
            for comment in entry['comments']:
                comment_entry.update(comment)
                renderer.outputTemplate(output, comment_entry, 'comment')
            if (form.has_key('preview')
                and renderer.flavour.has_key('comment-preview')):
                com = build_preview_comment(form, entry, config)
                renderer.outputTemplate(output, com, 'comment-preview')
            renderer.outputTemplate(output, entry, 'comment-form')
        args['template'] = template +u"".join(output)

    entry['num_comments'] = getCommentCount(entry, config)
    return template
