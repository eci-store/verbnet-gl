#!/usr/bin/python

import os
import sys
import getopt
import lxml
from lxml import etree

DEFAULT_SCHEMA = "vn_schema-3.xsd"

def validate_dir(dir_name, schema=DEFAULT_SCHEMA):
    for f in os.listdir(dir_name):
        if ".xml" in f:
            validate(f, schema)
    
                 
def validate(file_name, schema=DEFAULT_SCHEMA):    
    data = "\n".join([l for l in open(DEFAULT_SCHEMA)])
    schema_root = etree.XML(data)
    schema = etree.XMLSchema(schema_root)

    try:
        doc = etree.parse(open(file_name))
    except lxml.etree.XMLSyntaxError, e:
        print "!-----!"
        print file_name + " isn't even valid XML. C'mon now."
        print e
        print "!-----!"
        return None
    
    try:
        schema.assertValid(doc)
    except lxml.etree.DocumentInvalid, e:
        print "!-----!"
        print file_name
        print e
        print "!-----!"

#Main method as suggested by van Rossum, simplified
def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        opts, args = getopt.getopt(argv[1:], "h", ["help"])
    except:
        print "Error in args : " + str(argv[1:])
        return 2

    #Use opts and args here
    # ....
    for a in args:
        if os.path.isdir(a):
            validate_dir(a)
        else:    
            validate(a)
    
if __name__ == "__main__":
    sys.exit(main())
