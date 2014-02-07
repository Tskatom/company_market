#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import urllib2
import urllib
import argparse

URL = "http://ichart.finance.yahoo.com/"

class Yahoo(object):
    def get_price(self, symbol, start, end):
        """
        Extract parameters:
        a: start month, b: start day, c: start year
        d: end month, e: end day, f: end year
        """
        c, a, b = start.split("-")
        f, d, e = end.split("-")
        #month need to be set a current month - 1
        a = "%02d" % (int(a) - 1)
        d = "%02d" % (int(d) - 1)
        paras = {"a": a, "b": b, "c": c, "d": d, "e": e, "f": f,
                 "g": "d", "ignor": ".csv", "s": symbol}
        url = urllib2.urlparse.urljoin(URL, "table.csv?%s" % urllib.urlencode(paras))
        #start to download the data
        result = urllib2.urlopen(url).read()
        return result

