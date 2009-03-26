"""
Copyright (c) 2003-2005 Wari Wahab, Ted Leung

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

Implements the blogger xmlrpc interface.  Adds methods for:

   blogger.newPost:
       - appkey    (string)
       - blogid    (string)
       - username  (string)
       - password  (string)
       - content   (string)
       - publish   (boolean)
   
   blogger.editPost:
       - appkey    (string)
       - postid    (string)
       - username  (string)
       - password  (string)
       - content   (string)
       - publish   (boolean)

   blogger.getUsersBlogs:
       - appkey    (string)
       - username  (string)
       - password  (string)

   blogger.getUserInfo:
       - appkey    (string)
       - username  (string)
       - password  (string)

   blogger.deletePost:
   blogger.getRecentPosts:


If the configuration parameter config['xmlrpc_blogger_metaweblog']
is set to 'True' then blogger.getUsersBlogs returns one blog, otherwise
it returns one blog for each category.   If you are using a metaweblog
enabled client, you should probably set xmlrpc_blogger_metaweblog to 'True'

"""
import os, xmlrpclib, re
from Pyblosxom import tools, plugin_utils

LINEFEED = os.linesep


def verify_installation(request):
    config = request.getConfiguration()
    retval = 1

    # all config properties are optional
    if not config.has_key('xmlrpc_blogger_metaweblog'):
        print("missing optional property: 'xmlrpc_blogger_metaweblog'")

    return retval

def cb_xmlrpc_register(args):
    """
    Binds the methods that we handle with the function instances.
    """
    args["methods"].update( 
          { "blogger.getUserInfo": blogger_getUserInfo,
            "blogger.getUsersBlogs": blogger_getUsersBlogs,
            "blogger.getRecentPosts": blogger_getRecentPosts,
            "blogger.newPost": blogger_newPost,
            "blogger.editPost": blogger_editPost,
            "blogger.deletePost": blogger_deletePost })

    return args

def authenticate(request, username, password):
    """
    Handles authentication.  This works by getting the xmlrpc dispatcher
    plugin Python module and then calling authenticate on that.

    @param request: the pyblosxom Request instance
    @type  request: Request

    @param username: the username
    @type  username: string

    @param password: the password
    @type  password: string
    """
    xmlrpc_plugin = plugin_utils.get_plugin_by_name("xmlrpc")
    xmlrpc_plugin.authenticate(request, username, password)

def blogger_newPost(request, appkey, blogid, username, password, content,
        publish=1):
    """
    Used for creating new posts on the server
    """
    authenticate(request, username, password)

    config = request.getConfiguration()
    if os.path.isdir(os.path.normpath(os.path.join(config['datadir'],
            blogid[1:]))):
        # Look at content
        blogTitle = content.split(LINEFEED)[0].strip()

        tempMarker = (not publish and '-' or '')
        blogID = os.path.normpath(
            os.path.join(
                config['datadir'], blogid[1:] +
                re.sub('[^A-Za-z0-9]','_',blogTitle) + '.txt' +
                tempMarker
            )
        )
        if os.path.isfile(blogID) or os.path.isfile(blogID + '-'):
            # Generate a ficticious blog name
            blogID = os.path.normpath(
                os.path.join(
                    config['datadir'], blogid[1:] +
                    re.sub('[^A-Za-z0-9]','_',blogTitle) +
                    tools.generateRandStr() + '.txt' + tempMarker
                )
            )
        open(blogID, 'w').write(content.encode(config['blog_encoding']))

        # Generate BlogID
        return blogID.replace(config['datadir'], '')
    else: 
        raise xmlrpclib.Fault('PostError','Blog %s does not exist' % blogid)

def blogger_editPost(request, appkey, postid, username, password, content,
        publish=1):
    """
    Edit an existing post
    """
    authenticate(request, username, password)
    config = request.getConfiguration()
    filename = os.path.normpath(os.path.join(config['datadir'], postid[1:]))
    if publish and re.search(r'-$', filename):
        switchTo = re.sub(r'-$','',filename)
    elif not publish and re.search(r'txt$', filename):
        switchTo = filename + '-'
    else:
        switchTo = filename
    cache_driver = tools.importName('Pyblosxom.cache', 
            config.get('cacheDriver', 'base'))
    cache = cache_driver.BlosxomCache(request, config.get('cacheConfig', ''))
    # Check if file exists or not, edit everything here
    if os.path.isfile(filename):
        if filename != switchTo:
            if cache.has_key(filename):
                del cache[filename]
            os.remove(filename)

            if os.path.isfile(switchTo):
                basefilename, ext = os.path.splitext(os.path.basename(switchTo))
                dirname = os.path.dirname(switchTo)
                switchTo = os.path.normpath(
                    os.path.join(
                        config['datadir'], dirname[1:] + basefilename +
                        tools.generateRandStr() + ext
                    )
                )
        open(switchTo, 'w').write(content)
                
        return xmlrpclib.True
    else:
        raise xmlrpclib.Fault('UpdateError','Post does not exist')


def blogger_getUsersBlogs(request, appkey, username, password):
    """
    Returns trees below datadir
    """
    authenticate(request, username, password)
    config = request.getConfiguration()
    url = config.get('base_url', '')
    result = [{'url': url + '/', 'blogid': '/', 'blogName': '/'}]
    for directory in tools.Walk(request, config['datadir'], 0, re.compile(r'.*'), 1):
        blogpath = directory.replace(config['datadir'], '') + '/'
        blogpath = blogpath.replace(os.sep, '/')
        result.append({'url' : url + blogpath, 
                       'blogid' : blogpath, 
                       'blogName':blogpath})
    if config.get('xmlrpc_blogger_metaweblog','') == 'True':
        return result[:1]
    else:
        return result

def blogger_getUserInfo(request, appkey, username, password):
    """
    Useless Get user information feature
    """
    authenticate(request, username, password)
    # Change these values? Not that important unless some apps needs it.
    config = request.getConfiguration()
    url = config.get('base_url', '')
    return {'firstname':'Ficticious',
            'lastname':'User',
            'userid':'01',
            'email':'someuser@example.com',
            'nickname':'pyblosxom',
            'url':url}

def blogger_deletePost(request, appkey, postid, username, password, publish):
    """
    Delete an existing post
    """
    # Really want to implement this? hmmm
    authenticate(request, username, password)
    config = request.getConfiguration()
    url = config.get('base_url', '')
    cache_driver = tools.importName('Pyblosxom.cache', 
            config.get('cacheDriver', 'base'))
    cache = cache_driver.BlosxomCache(request, config.get('cacheConfig', ''))
    fn = os.path.normpath(os.path.join(config['datadir'], postid))

    data = request.getData()
    extensions = data['extensions']
    for e in extensions.keys():
        filename = fn+'.'+e
        if os.path.isfile(filename):
            break
            
    if os.path.isfile(filename):
        if cache.has_key(filename):
            del cache[filename]
        os.remove(filename)
        return xmlrpclib.True
    else:
        raise xmlrpclib.Fault('DeleteError','Post does not exist')

def blogger_getRecentPosts(request, appkey, blogid, username, password,
        numberOfPosts=5):
    """
    Get recent posts from a blog tree
    """
    authenticate(request, username, password)
    config = request.getConfiguration()
    data = request.getData()
    from Pyblosxom.entries.fileentry import FileEntry
    from Pyblosxom import pyblosxom

    exts = tools.run_callback("entryparser",
                {'txt': pyblosxom.blosxom_entry_parser},
                mappingfunc=lambda x,y:y,
                defaultfunc=lambda x:x)

    data['extensions'] = exts
    
    result = []
    dataList = []
    filelist = tools.Walk(request, os.path.join(config['datadir'], blogid[1:]), 
            pattern = re.compile(r'.*\.(' +
            '|'.join(exts.keys()) + ')-?$'), 
            recurse = 1)
    for ourfile in filelist:
        entry = FileEntry(request, ourfile, config['datadir'])
        dataList.append((entry._mtime, entry))

    # this sorts entries by mtime in reverse order.  entries that have
    # no mtime get sorted to the top.
    dataList.sort()
    dataList.reverse()
    dataList = [x[1] for x in dataList]
    
    count = 1
    for entry in dataList:
        result.append({'dateCreated' : xmlrpclib.DateTime(entry['mtime']),
                       'userid' : '01',
                       'postid' : entry['filename'].replace(
                                  config['datadir'],''),
                       'content' : open(entry['filename']).read()})
        if count >= int(numberOfPosts):
            break
        count += 1
    return result

# vim: tabstop=4 expandtab shiftwidth=4
