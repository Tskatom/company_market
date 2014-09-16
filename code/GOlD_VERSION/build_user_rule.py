#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import argparse

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--users', type=str)
    ap.add_argument('--out', type=str)
    return ap.parse_args()

def main():
    arg = parse_args()
    user_file = arg.users
    rule_file = arg.out
    with open(user_file, "r") as ur, open(rule_file, "w") as rw:
        for line in ur:
            user, count = line.strip().split("\t")
            delta = 24 * 30 if int(count) > 100 else 0
            term = "from:%s" % user
            rw.write("%s|%d|%s\n" %(user, delta, term))

if __name__ == "__main__":
    main()

