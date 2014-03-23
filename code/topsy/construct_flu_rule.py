#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os

rule = set('"'+item.strip()+'"' for item in open(sys.argv[1]))
if len(sys.argv) > 2:
    s_rule = set('"'+item.strip()+'"' for item in open(sys.argv[2]))
else:
    s_rule = set()

with open("vehicle_components_rule.txt", "w") as w:
    for item in rule:
        delta = 24 
        if item in s_rule:
            continue
        w.write("%s|%d|%s\n" % (item.replace('"', "").replace(" ","_"), delta, item.strip().lower()))

if __name__ == "__main__":
    pass

