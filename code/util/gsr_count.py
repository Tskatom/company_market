#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import json
import argparse

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gsr', type=str,
            help='gsr folder')
    ap.add_argument('--out', type=str,
            help='count output')
    arg = ap.parse_args()
    return arg

def main():
    arg = parse_args()
    gsr_fold = arg.gsr
    output = arg.out
    gsr_count = {}
    files = [os.path.join(gsr_fold, f) for f in os.listdir(gsr_fold)]
    for f in files:
        with open(f) as tf:
            for line in tf:
                event = json.loads(line)
                date = event["eventDate"][0:10]
                gsr_count.setdefault(date, 0)
                gsr_count[date] += 1
    sort_days = sorted(gsr_count.keys())
    with open(output, "w") as ot:
        for day in sort_days:
            ot.write("%s\t%d\n" % (day, gsr_count[day]))

if __name__ == "__main__":
    main()

