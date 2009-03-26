"""
noindex : hide specified story in index.

To make a story hidden, insert below line to second line:
#noindex 1
"""
__author__ = "hylom - hylom <at> sourceforge.jp"
__version__ = "$Id: noindex.py,v 1.3 2008/12/15 13:46:35 hylom Exp $"
__url__ = "http://hylom.sakura.ne.jp/"
__description__ = "hide specified story in index."

from Pyblosxom import tools
import string, os

def verify_installation(request):
    # there's no configuration needed for this plugin.
    return 1

def cb_prepare(args):
    request = args["request"]
    query = request.getHttp().get('QUERY_STRING', '')
    path_info = request.getHttp().get('PATH_INFO', '')

#    logger = tools.getLogger()
    
    data = request.getData()
    if len(data['entry_list']) != 1:
        data["entry_list"] = filter(lambda e: not e.has_key('noindex'), data["entry_list"])
    else:
        file_path = path_info.strip("/")
        req_path = data["entry_list"][0]["absolute_path"].strip("/")

        if req_path == file_path:
            data["entry_list"] = filter(lambda e: not e.has_key('noindex'), data["entry_list"])

