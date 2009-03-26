#!/usr/bin/env python
"""
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
__version__ = "$Id: mt2blosxom.py,v 1.1.1.1 2008/11/27 17:15:38 hylom Exp $"


import sys, time, os, re, random

entryDelim = re.compile( r"^--------$", re.MULTILINE )
sectionDelim = re.compile( r"^-----$", re.MULTILINE )

DEFAULTBREAKS = 1

def convert(inputfile, output_dir_root):    
    input = open(inputfile).read()
    entries = entryDelim.split(input)
    for entry in entries:
        if entry.strip():
            sections = sectionDelim.split(entry)
            body = sections[1].split(":",1)[1]
            #lee.list@joramo.com 
            #2003-02-12 
            #    check to see if extended sections exist
            #    when exporting from Radio Userland to Moveable Typle
            #    no extendedbody is created
            extendedbody = ""
            if len(sections) > 2:
                extendedbody = sections[2].split(":",1)[1]
            fields = sections[0].strip().split("\n")
            publish = 0
            body = sections[1].split(":",1)[1]
            #lee.list@joramo.com 
            #2003-02-12 
            #     Radio Userland -> MT export
            #     may not include all fields, so need to to preset
            title = "<!-- No Title -->"
            date = "01/01/2000 00:01:00 AM"
            category = ""
            author = ""
            publish = 1
            breaks = DEFAULTBREAKS
            for field in fields:
                if field.strip():
                    tag, value = field.split(": ", 1)
                    if tag == "TITLE":
                        title = value.strip()
                    elif tag == "DATE":
                        date = value.strip()
                    elif tag == "CATEGORY":
                        category = value.strip()
                    elif tag == "AUTHOR":
                        author = value.strip()
                    elif tag == "CONVERT BREAKS":
                        breaks = value.strip()
                    elif tag == "STATUS":
                        publish = 0
                        if value.strip().lower() == "publish":
                            publish = 1
            #lee.list@joramo.com
            #2003-02-12
            #try to a variety of time formats
            timeformats = ("%m/%d/%Y %H:%M:%S %p", "%m/%d/%y %H:%M:%S %p")
            for timeformat in timeformats:
                formatmatched = 0
                try:
                    timestamp = time.mktime(time.strptime(date, timeformat))
                    formatmatched = 1
                except:
                    continue
                if formatmatched == 1:
                    break
            if formatmatched == 0:
                raise ValueError, "timeformat not matched\n"+date

            output_directory = output_dir_root+"/"+category
            if not os.path.exists(output_directory):
                os.mkdir(output_directory, 0755)
            
            outputfile = title.strip()
            if not outputfile: outputfile = body[:20].strip()

            outputfile= "%s/%s" % (output_directory, re.sub(r"[^a-zA-Z0-9]", "_", outputfile))
            

            if os.path.isfile(outputfile + ".txt") or os.path.isfile(outputfile + ".txt-"):
                outputfile = outputfile + str(random.random()).split(".")[1]
            if publish:
                outputfile = outputfile + ".txt"
            else:
                outputfile = outputfile + ".txt-"

            output = open(outputfile, "w")
            output.write(title+"\n")
            if breaks:
                output.write('#parser linebreaks\n')
            output.write("<!--timestamp:%s:-->"%timestamp)
            output.write("<!--category:%s:-->"%category)
            output.write("<!--author:%s:-->"%author)
            output.write(body)
            output.write(extendedbody)
            output.close()
            # set the modified date on the output file
            os.utime(outputfile, (timestamp, timestamp)) 
if __name__=="__main__":
    try:
        inputfile, output_dir_root = sys.argv[1:]
    except:
        print """Usage: mt2blosxom mtexportfile datadir
        mtexportfile - File containing exported Movable Type entries
        datadir -  Blosxom directory to put files in"""
        sys.exit(0)

    convert(inputfile, output_dir_root)

