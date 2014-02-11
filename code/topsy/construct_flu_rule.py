#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os

rule = set('"'+item.strip()+'"' for item in open(sys.argv[1]))

with open("Flu_rule.txt", "w") as w:
    for item in rule:
        w.write("%s|%s\n" % (item.replace('"', "").replace(" ","_"), item))

if __name__ == "__main__":
    pass

