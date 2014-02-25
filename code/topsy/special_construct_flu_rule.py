#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os

rule = set('"'+item.strip()+'"' for item in open(sys.argv[1]))
s_rule = set('"'+item.strip()+'"' for item in open(sys.argv[2]))

with open("Special_flu_rule.txt", "w") as w:
    for item in rule:
        delta = 1 
        if item not in s_rule:
            continue
        w.write("%s|%d|%s\n" % (item.replace('"', "").replace(" ","_"), delta, item))

if __name__ == "__main__":
    pass

