#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import argparse

ap = argparse.ArgumentParser()
ap.add_argument('--rule', type=str)
ap.add_argument('--spec', type=str)
ap.add_argument('--out', type=str)
arg = ap.parse_args()

rule = set('"'+item.strip()+'"' for item in open(arg.rule))
if arg.spec:
    s_rule = set('"'+item.strip()+'"' for item in open(sys.argv[2]))
else:
    s_rule = set()

with open(arg.out, "w") as w:
    for item in rule:
        delta = 6 
        if item in s_rule:
            continue
        w.write("%s|%d|%s\n" % (item.replace('"', "").replace(" ","_"), delta, item))

if __name__ == "__main__":
    pass

