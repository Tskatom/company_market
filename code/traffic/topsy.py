#!/usr/bin/python
# -*- coding:utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"


_APIKEY = '09C43A9B270A470B8EB8F2946A9369F3'
_URL = 'http://api.topsy.com/v2/content/bulktweets.json?'


import urllib2
import urllib
import logging
import os
import sys
from datetime import datetime, timedelta


logging.basicConfig(filename='topsy.log', level=logging.INFO)

def ingest(start, end, rule, out_file):
	param = {}
	param["apikey"] = _APIKEY
	param["limit"] = 20000
	param["sample"] = 100
	param["include_metrics"] = 1
	param["q"] = rule

	informat = "%Y-%m-%d"
	outformat = "%s"
	start_epco = datetime.strptime(start, informat).strftime(outformat)
	end_epco = datetime.strptime(end, informat).strftime(outformat)

	param["mintime"] = start_epco
	param["maxtime"] = end_epco

	target_url = _URL + urllib.urlencode(param)
	print target_url

	result = urllib2.urlopen(target_url)

	with open(out_file, "w") as ow:
		ow.write(result.read())

def crawl():
	start = "2013-01-01"
	rule = "'3D Systems' OR $DDD"
	terminal = "2013-04-01"
	company = "DDD"
	out_dir = "/home/weiwang/workspace/data"
	end = start
	while end < terminal:
		try:
			end = (datetime.strptime(start, "%Y-%m-%d") + timedelta(days=15)).strftime("%Y-%m-%d")
			if end > terminal:
				end = terminal
			out_file = os.path.join(out_dir, "%s_%s_%s" % (company, start, end))
			print start, end
			ingest(start, end, rule, out_file)
			start = end

		except:
			logging.warning("Error:[%s]" % sys.exc_info()[0])
			start = end

if __name__ == "__main__":
	crawl()	




