#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import sys,os,re,codecs
import HTMLTagFilter

sys.stdin = codecs.getreader('utf_8')(sys.stdin)
sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

alist = ["a", "a:href", "a:name" ]
dlist = ["*"]

tag_filter = HTMLTagFilter.HTMLTagFilter( HTMLTagFilter.DENY_ALLOW, alist, dlist )

def make_hashlist( path_img_hash ):
	"""
	create hash list.
	"""
	try:
		file_img_hash = open( path_img_hash, "r" )
	except IOError:
		sys.stderr.write("cannot open file: %s" % path_img_hash)
		return None;

	hashlist = {};
	for line in file_img_hash:
		splited = line.strip().split( "\t", 2)
		# hashlist's format: <hash> \t <filename>
		hashlist[splited[1]] = splited[0]

	return hashlist;


def default_markup_rule( line ):
	"""
	apply default markup rules.
	"""
#	line = re.sub( ur"&", ur"&amp", line )
#	line = re.sub( ur"<", ur"&lt;", line )
#	line = re.sub( ur">", ur"&gt;", line )
	line = tag_filter.apply(line)
	line = re.sub( ur"★(表[0-9～]+)", ur"<b>\1</b>", line )
	line = re.sub( ur"★(図[0-9～]+)", ur"<b>\1</b>", line )
	line = re.sub( ur"★(リスト[0-9～]+)", ur"<b>\1</b>", line )
	line = re.sub( ur"★b\[(.*?)\]", ur"<b>\1</b>", line )

	line = re.sub( ur"★\[(\S*) (.*?)\]", r'<a href="\1">\2</a>', line )

	if re.search( ur"^☆#", line ):
		line = ""

	return line

####### markup subroutines ########

def ulist( line ):
	stream_in = sys.stdin
	print "<ul>"
	while re.search( ur"^・", line):
		print re.sub( ur"^・(.*)$", ur"<li>\1</li>", line.strip() )
		line = stream_in.readline()
	print "</ul>\n"

def begin_column( line ):
	try:
		str_title = re.search( ur"^☆begin-column:(.*)$", line ).group(1)
	except AttributeError:
		str_title = ""

	html = """<table bgcolor="#DDDDDD" border="0" cellpadding="6" width="95%%">
<tr><th>%s</th></tr>
<tr><td><span style="font-size: 85%%;">
""" % (str_title)
	print html

def end_column( line ):
	print """</span></td></tr>
</table>
"""

def list_start():
  return "<pre>"

def list_end():
  return "</pre>"

def list( line ):
	stream_in = sys.stdin
	try:
		str_title = re.search( "^☆(リスト.*)$", line ).group(1)
	except AttributeError:
		str_title = ""
	print "<p><b>%s</b></p>" % (str_title)
	print list_start(line)

	for line in stream_in:
		line = line.strip()
		line = line.replace( "&", "&amp;" )
		line = line.replace( "<", "&lt;" )
		line = line.replace( ">", "&gt;" )
		if line == "----":
			break
		print line
	print list_end()

def code( line ):
	stream_in = sys.stdin
	print list_start()

	for line in stream_in:
#		line = line.strip()
		line = line.replace( "&", "&amp;" )
		line = line.replace( "<", "&lt;" )
		line = line.replace( ">", "&gt;" )
		line = line = re.sub( ur"★b\[(.*?)]", ur"<b>\1</b>", line )

		if re.search(ur"^☆\+---$", line):
			break
		print line,
	print list_end()


def inline( line ):
	stream_in = sys.stdin
	for line in stream_in:
#		line = line.strip()
		if re.search( ur"^☆}}}", line ):
			break
		print line


def comment( line ):
	stream_in = sys.stdin
	for line in stream_in:
		line = line.strip()
		if re.search( ur"^☆}}}", line ):
			break

def space( line ):
	print "<br><br>"


def fig_start( cap="" ):
	return """<table align="center" border="0" cellpadding="0" cellspacing="0">
<tr> <td valign="top" align="center">
"""

def fig_end( cap="" ):
	return """</td> </tr>
<tr> <td><span style="font-size: 80%%; font-weight: bold;">
%s
</span></td> </tr>
</table>
""" % (cap)

def fig( line, filehash ):
	stream_in = sys.stdin
	try:
		str_title = re.search( ur"^☆(図.*)$", line ).group(1)
	except AttributeError:
		str_title = ""
	print fig_start()

	line = stream_in.readline()
	hash = ""
	hash_s = ""
	match_o1 = re.search( ur"<([^,]*?)>", line )
	match_o2 = re.search( ur"<(.*?),\s*(.*?)>", line )
	if not match_o1 == None:
		imgname_s = re.sub( r"(.[A-Za-z0-9_]+)$", r"_s\1", match_o1.group(1) )
		hash = filehash.get(match_o1.group(1), "")
		hash_s = filehash.get(imgname_s, "")
		if hash_s == "":
			hash_s = filehash.get(match_o1.group(1), "")
	elif not match_o2 == None:
		hash = filehash.get(match_o2.group(1), "")
		hash_s = filehash.get(match_o2.group(2), "")

	print """<a href="/blob.pl?id=%s">
<slash type="image" id="%s" title="%s">
</a>
""" % (hash, hash_s, str_title)

	print fig_end( str_title );


def table_start( cap ):
	return """<table align="center" border="1" width="90%%">
<caption><b>%s</b></caption>
""" % cap

def table_end():
  return "</table>\n"

def table( line ):
	stream_in = sys.stdin
	str_title = ""
	try:
		str_title = re.search( ur"^☆(表.*)$", line ).group(1)
	except AttributeError:
		str_title = ""
	print table_start( str_title )

	num_row = 0
	table_contents = []
	for line in stream_in:
		line = line.strip(" \n")
		if re.search( ur"^\s*$", line ):
			break
		line = default_markup_rule( line )
		if re.search( ur"^〓", line ):
			line = re.sub( ur"^〓", "", line )
			tag_mode = "th"
		else:
			tag_mode = "td"
		table_contents.append([])
		num_col = 0
		for item in line.split( "\t" ):
			if item == "":
				if num_col == 0:
					n = 1
					try:
						while table_contents[num_row-n][num_col]["item"] == "":
							n += 1
						table_contents[num_row-n][num_col]["row"] += 1
					except IndexError:
						pass
				else:
					n = 1
					try:
						while table_contents[num_row][num_col-n]["item"] == "":
							n += 1
						table_contents[num_row][num_col-n]["col"] += 1
					except IndexError:
						pass

			table_contents[num_row].append( {"tag":tag_mode,"item":item,"row":1,"col":1} )
			num_col = num_col + 1
		num_row = num_row + 1

	for row_item in table_contents:
		line = "<tr>"
		for item in row_item:
			if item["item"] == "":
				continue
			line = line + "<" + item["tag"]
			if not item["row"] == 1:
				line = line + (' rowspan="%s"' % item["row"])
			if not item["col"] == 1:
				line = line + ( ' colspan="%s"' % item["col"] )
			line = line +  ">"
			line = line + item["item"]
			line = line + "</" + item["tag"] + ">"
		line = line + "</tr>\n"
		print line,
	
#			line = "<tr><th>" + re.sub( ur"^〓", "", line ) + "</th></tr>"
#			line = line.replace( "\t", "</th><th>" )
#			print line
#		else:
#			line = "<tr><td>" + line + "</td></tr>"
#			line = line.replace( "\t", "</td><td>" )
#			print line

	print table_end()


####### main routine ##########

str_usage = "markup.pl hashfile\n"

try:
	path_img_hash = sys.argv[1]
except IndexError:
	sys.stderr.write( str_usage )
	sys.exit(-1)

hashlist = make_hashlist(path_img_hash)

if hashlist == None:
	sys.stderr.write( str_usage )
	sys.exit(-1)

for line in sys.stdin:

	line = default_markup_rule( line )

    #head-of-line rules
	if re.search( ur"^☆{{{$", line ):
		inline(line)
		continue
	elif re.search( ur"^☆comment\s{{{$", line ):
		comment(line)
		continue
	elif re.search( ur"^・", line ):
		ulist(line)
		continue
	elif re.search( ur"^☆begin-column:", line ):
		begin_column(line)
		continue
	elif re.search( ur"^☆end-column", line ):
		end_column(line)
		continue
	elif re.search( ur"^☆space", line ):
		space(line)
		continue
	elif re.search( ur"^●", line ):
		line = re.sub( ur"^●(.*)$", ur"<h4>\1</h4>", line )
		print line
		continue
	elif re.search( ur"^○", line ):
		line = re.sub( ur"^○(.*)$", ur"<b>\1</b>", line )
		print line
		continue
	elif re.search( ur"^☆----", line ):
		line = re.sub( ur"☆----.*-{0,1}", u"<hr>", line )
		print line
		continue
	elif re.search( ur"^☆\+---", line ):
		code(line)
		continue
	elif re.search( ur"^☆表", line ):
		table(line)
		continue
	elif re.search( ur"^☆図", line ):
		fig(line, hashlist)
		continue
	elif re.search( ur"^☆リスト", line ):
		list(line)
		continue

	if re.search( ur"^　", line ):
		line = "<p>" + line + "</p>"

	if re.search( r"^\s*$", line ):
		line = ""

	print line

#end-of-loop


