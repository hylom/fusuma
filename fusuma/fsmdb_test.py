#!/usr/bin/env python

import sys
from fsmdb import fsmdb

tests = {}

    
def test_db1():
    """test for database creation."""
    db = fsmdb.FsmDbSQLite("./test.db")
    cols = ["test1", "test2", "test3"]
    types = ["integer not null", "char", "long"]
    db._create_table("test_table", cols, types)

tests["db1"] = test_db1

def test_fsmdb_orderd_dict():
    """test for FsmDbOrderdDict."""
    datas = ( ("foo", 1),
              ("bar", 100),
              ("hoge", "hogehoge") )
    dc = dict(datas)
    d = fsmdb.FsmDbOrderdDict(datas)
    print "foo:", d["foo"]
    print "bar:", d["bar"]
    print "hoge:", d["hoge"]
    print d.seq
#    dct = dict(datas)
#    for i in range(len(dct)):
#        if d[keys[i]] != values[i]:
#            print "error: d[%s] is not %s.\n" % (keys[i], values[i])

tests["od"] = test_fsmdb_orderd_dict

def test_db2():
    """test for create database with FsmDbOrderdDict"""
    defs = ( 
        ("col1", "integer primary key autoincrement"),
        ("col2", "char"),
        ("col3", "long") )
    db = fsmdb.FsmDbSQLite("./test.db")
    proto = fsmdb.FsmDbOrderdDict(defs)
    db.create_table("test_table", proto)
    db.close()
#    defs = ( 
#        ("col2", "string1"),
#        ("col3", 2.01) )
#    param = fsmdb.FsmDbOrderdDict(defs)
#    db.insert("test_table", param)
tests["db2"] = test_db2

def test_insert():
    """test for insert database with FsmDbOrderdDict"""
    defs = ( 
        ("col2", "string1"),
        ("col3", 2.01) )
    param = fsmdb.FsmDbOrderdDict(defs)
    db = fsmdb.FsmDbSQLite("./test.db")
    db.insert("test_table", param)
    db.commit()
    db.close()
tests["ins"] = test_insert

def test_select():
    """test for select database with FsmDbOrderdDict"""
    db = fsmdb.FsmDbSQLite("./test.db")
    cur = db.select("test_table")
    for row in cur:
        print row
    cur.close()
    db.close()
tests["sel"] = test_select

try:
    test = sys.argv[1]
except IndexError:
    sys.exit( "usage: %s test" % sys.argv[0])

if not tests.get(test, None):
    print >> sys.stderr, "test %s is not defined.\n" % test
    print >> sys.stderr, "available test:"
    for teststr in tests.keys():
        print teststr
    sys.exit()

print >> sys.stderr, tests[test].__doc__
tests[test]()

