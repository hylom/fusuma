# vim: tabstop=4 shiftwidth=4 expandtab
"""
Generic wiki markup PreFormatter 2002-11-18, for pyblosxom
CHANGE wikibaseurl to point to your wiki, & wikinamepattern to yours
Bug reports, comments, presents, etc. to John Abbe at johnca@ourpla.net
ToDo: Lists; code/<pre>; InterWiki links; other wikinamepatterns

You can configure this as your default preformatter by configuring it in your
L{config} file as follows::

    py['parser'] = 'genericwiki'

or in your blosxom entries, place a C{#parser wiki} line after the title of
your blog::

    My Little Blog Entry
    #parser genericwiki
    This is a text in '''wiki''' format

This preformatter also supports WikiWirds, you need to point out where your
Wiki site is. This is configured with a new variable in your config.py file,
'genericwiki_baseurl'::

    py['genericwiki_baseurl'] = 'http://www.google.com/search?q='

The above example would expand 'WikiWord' to
http://www.google.com/search?q=WikiWord

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

Copyright 2004, 2005 John Abbe
"""
__author__ = 'John Abbe <johnca at ourpla dot net>'
__version__ = "$Id: genericwiki.py,v 1.1.1.1 2008/11/27 17:15:38 hylom Exp $"
PREFORMATTER_ID = 'genericwiki'
import re

def cb_preformat(args):
    """
    Preformat callback chain looks for this.

    @param args: a dict with 'parser' string and a list 'story'
    @type args: dict
    """
    if args['parser'] == PREFORMATTER_ID:
        config = args['request'].getConfiguration()
        baseurl = config.get('genericwiki_baseurl', None)
        return parse(''.join(args['story']), baseurl)


def parse(text, wikibaseurl):
    """
    The main workhorse that convert wiki text into html markup

    @param text: Text for conversion
    @type text: string
    """
    # WikiName pattern used in your wiki
    wikinamepattern = r'\b(([A-Z]+[a-z]+){2,})\b' # original
    mailurlpattern = r'mailto\:[\"\-\_\.\w]+\@[\-\_\.\w]+\w'
    newsurlpattern = r'news\:(?:\w+\.){1,}\w+'
    fileurlpattern = r'(?:http|https|file|ftp):[/-_.\w-]+[\/\w][?&+=%\w/-_.#]*'

    # Turn '[xxx:address label]' into labeled link
    text = re.sub(r'\[(' +
           fileurlpattern + '|' +
           mailurlpattern + '|' +
           newsurlpattern + ')\s+(.+?)\]',
           r'<a href="\1">\2</a>', text)

    # Convert naked URLs into links -- skip ones with a " before
    text = re.sub(r'(?<!")(' +
           newsurlpattern + '|' +
           fileurlpattern + '|' +
           mailurlpattern + ')',
           r'<a href="\1">\1</a>', text)

    # Convert WikiNames into links
    if wikibaseurl:
        text = re.sub(r'(?<![\?\/\=])' +
               wikinamepattern, '<a href="' +
               wikibaseurl + r'\1">\1</a>', text)

    # '' for emphasis, ''' for strong, ---- for a horizontal rule
    text = re.sub(r"'''(.*?)'''", r"<strong>\1</strong>", text)
    text = re.sub(r"''(.*?)''", r"<em>\1</em>", text)
    text = re.sub(r"\n(-{4,})\n", "<hr>", text)

    # Convert two or more newlines into <p>
    text = re.sub(r'\n{2,}', r'</p>\n<p>', text)

    return "<p>" + text + "</p>"

if __name__ == '__main__':
    text = """This is a test
    To test the wiki

    [http://roughingit.subtlehints.net/pyblosxom?blah=duh#spam A link]
    news:roughingit.subtlehints.net/pyblosxom/ - no, ''I'' do '''not''' have a news
    server.  mailto:wari@example should go link to an email.  WikiWiki is a wiki
    Keyword
    """
    print parse(text, 'http://wiki.subtlehints.net/moin/')
