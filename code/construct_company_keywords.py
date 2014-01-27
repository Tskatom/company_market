#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import json

company_file = open(sys.argv[1])
symbols = company_file.readline().split("\t")[1:]
ticks = company_file.readline().split()[1:]


keywords = {}
for i, symbol in enumerate(symbols):
    company = symbol.split(" ")[0].lower()
    tick = ticks[i].split(":")[1].lower()
    keywords["$%s" % company] = company
    keywords["#%s" % company] = company
    keywords["$%s" % tick] = company
    keywords["#%s" % tick] = company

json.dump(keywords, open("company_keywords.json", "w"))

company_file.close()
