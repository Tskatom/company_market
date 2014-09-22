#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os

keywords_file = "../data/Company_search_keywords.csv"
out_rule_file = "../data/Company_search_rule.txt"

start = "2009-01-01"
end = "2014-09-01"
with open(keywords_file) as kf, open(out_rule_file, "w") as orf:
    for line in kf:
        try:
            name, word = line.replace("\n","").split("\t") #using tab as separator
        except:
            print line
            sys.exit()
        #rule format: name|startDay|endDay|searchWindows(Hour Unit)|search_rule
        if len(word) == 0:
            search_text = "$%s" % name
        else:
            search_text = '$%s OR "%s"' % (name, word)
        search_term = "%s|%s|%s|%d|%s\n" % (name, start, end, 24, search_text)
        orf.write(search_term)

if __name__ == "__main__":
    pass

