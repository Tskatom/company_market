#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import yahoo
import argparse

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", type=str, help="company symbol")
    ap.add_argument("--start", type=str, help="start date")
    ap.add_argument("--end", type=str, help="end date")
    ap.add_argument("--out", type=str, default="." + os.sep, help="output dir")
    arg = ap.parse_args()
    return arg


def main():
    arg = parse_args()
    iyahoo = yahoo.Yahoo()
    try:
        data = iyahoo.get_price(arg.symbol, arg.start, arg.end)
        if data:
            with open(os.path.join(arg.out, "%s.csv" % arg.symbol), "w") as w:
                w.write(data)
    except:
        print sys.exc_info()[0]


if __name__ == "__main__":
    main()

