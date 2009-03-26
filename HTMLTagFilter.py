#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

DENY_ALLOW = 0
ALLOW_DENY = 1
#str_regex_tag = r"""[^"'<>]*(?:"[^"]*"[^"'<>]*|'[^']*'[^"'<>]*)*(?:>|(?=<)|$(?!＼n))"""
#str_regex_comment =r'<!(?:--[^-]*-(?:[^-]+-)*?-(?:[^>-]*(?:-[^>-]+)*?)??)*(?:>|$(?!＼n)|--.*$)'


class HTMLTagFilter:
	"""
	allow / deny list:
	a -> <a>
	a:href -> <a href>
	a:* -> a tag's any attribute
	*:style -> any tag's style attribute
	"""

	def __init__(self, rule, allow_list, deny_list):
		"""
		create new object.
		
		@param rule: filtering rule. DENY_ALLOW or ALLOW_DENY.
		@type rule: int
		
		@param allow_list: allowed tag/attribute's list.
		@type allow_list: sequence
		
		@param deny_list: denied tag/attribue's list.
		@type deny_list: sequece
    	"""
		self.rule = rule
		self.allow_list = allow_list[:]
		self.deny_list = deny_list[:]

		allow_tuple = self._create_filtering_rule( allow_list )
		deny_tuple = self._create_filtering_rule( deny_list )

		self.allow_attributes = allow_tuple[0]
		self.allow_elements = allow_tuple[1]
		self.deny_attributes = deny_tuple[0]
		self.deny_elements = deny_tuple[1]


	def _create_filtering_rule( self, rule_list ):
		attr_map = {}
		elem_list = []
		for item in rule_list:
			item = item.strip()
			if item.find(":") == -1 : # element rule
				elem_list.append( item )
			else: # attribute rule
				match_obj = re.search( r"^(\w*|\*):(\w*|\*)$", item )
				elem = match_obj.group(1)
				attr = match_obj.group(2)

				if elem == "":
					elem = "*"
				if attr == "":
					attr = "*"

				attr_list = attr_map.get( elem, [] )
				attr_list.append( attr )
				attr_map[elem] = attr_list
		return (attr_map, elem_list)

	def apply( self, str ):
		"""
		apply filter rule to string.
		return string's filtered copy.
		
		@param str: target string
		@type str:  string
		"""
		ret_str = ""
		str_regex_split = r"""(<[^"'<>]*(?:"[^"]*"[^"'<>]*|'[^']*'[^"'<>]*)*(?:>|(?=<)|$(?!\n)))"""
		str_regex_tag = r"""^<.*>$"""
		regex_split = re.compile( str_regex_split )
		regex_tag = re.compile( str_regex_tag )
		splitted_list = regex_split.split( str )
		
		for term in splitted_list:
			if regex_tag.search( term ):
				term = self.filter_tag( term )
			else:
				term = self.quote(term)
			ret_str = ret_str + term
				
		return ret_str

	def filter_tag( self, str ):
#		print str + ":"
		match_obj = re.search( r"^<(/{0,1}\s*\w+)\s*(.*)>", str )
		tag = ""
		attr_list = []
		if match_obj:
			tag = match_obj.group(1)
			attr = match_obj.group(2).strip()
			if not attr == "":
				attr_list = re.split( "\s+", attr )

		# element filtering
		tag = tag.replace( "/", "")
		if self._check( tag, self.allow_elements, self.deny_elements ):
			str = self.quote( str )
			return str

		# attribute filtering
		new_list = []
		for item in attr_list:
			(attr, val) = item.split( "=", 1 )
			allow_list = self.allow_attributes.get(tag, [] )
			deny_list = self.deny_attributes.get(tag,[] )

			if not self._check( attr, allow_list, deny_list ):
				new_list.append(item)

		if len(new_list) > 0:
			str = "<" + tag + " " + " ".join( new_list ) + ">"
		else:
			str = "<" + tag + ">"
		return str
	    
	def _check( self, str, allow_list, deny_list ):
		is_allow = ( str in allow_list ) or ( "*" in allow_list )
		is_deny = ( str in deny_list ) or ( "*" in deny_list )
		if self.rule == ALLOW_DENY:
			if (not is_allow) or (is_deny):
				return 1
		elif self.rule == DENY_ALLOW:
			if (is_deny) and (not is_allow):
				return 1
		return 0

	def quote( self, str ):
		str_ret = str.replace( "&", "&amp;" )
		str_ret = str_ret.replace( "<", "&lt;" )
		str_ret = str_ret.replace( ">", "&gt;" )
		return str_ret


#testcode
#alist = ["a", "b", "br", "p", "a:href" ]
#dlist = ["*"]
#filter = HTMLTagFilter( DENY_ALLOW, alist, dlist)
#str = """hoge > hoge < hoge<a href="URL" style="<"><b>test</b><br>"""


# print "allow-elem:"
# for item in filter.allow_elements:
# 	print item
# print "deny-elem:"
# for item in filter.deny_elements:
# 	print item

# print "allow-attr:"
# for elem in filter.allow_attributes:
# 	for attr in filter.allow_attributes[elem]:
# 		print "%s : %s" % (elem, attr)
# print "deny-attr:"
# for elem in filter.deny_attributes:
# 	for attr in filter.deny_attributes[elem]:
# 		print "%s : %s" % (elem, attr)



#print "Input: %s" % str
#print filter.apply(str)
