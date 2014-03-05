#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os

rule = set('"'+item.strip()+'"' for item in open(sys.argv[1]))
s_rule = set('"'+item.strip()+'"' for item in open(sys.argv[2]))

print rule

print s_rule
with open("Special_flu_rule.txt", "w") as sw, open("Normal_flu_rule.txt", "w") as nw:
    for item in rule:
        delta = 1 
        if item not in s_rule:
            nw.write("%s|%d|%s\n" % (item.replace('"', "").replace(" ", "_"), 24, item))
        else:
            sw.write("%s|%d|%s\n" % (item.replace('"', "").replace(" ","_"), delta, item))

if __name__ == "__main__":
    pass

