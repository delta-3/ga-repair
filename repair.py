#!/usr/bin/env python
import sys


def parse_int(i):
    int(i)

def load_filters():
    f = open ("filters.txt")
    return f.readlines()


def should_block():
    pass

if __name__ == "__main__":

    i = sys.argv[1]
    if not(should_block()):
        try: 
            parse_int(i)
        except Exception as e:
            print e

    else:
        print "Input %s blocked" % str(i)
