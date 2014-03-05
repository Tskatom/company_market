#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
from datetime import timedelta, datetime
import calendar

start_month = "2013-01"
end_month = "2014-01"

def add_month(year_month, num):
    year, month = map(int, year_month.split("-"))
    month = month - 1 + num
    year = year + month / 12

    month = month % 12 + 1
    return "%d-%02d" % (year, month)
shells = []
cursor = start_month
while cursor <= end_month:
    year, month = map(int, cursor.split("-"))
    start = "%s-%s" % (cursor, "01")
    end = "%s-%d" %(cursor, calendar.monthrange(year, month)[1])

    out = os.path.join(sys.argv[1], cursor.replace("-", ""))
    command = "python multithread_topsy.py %s $1 %s %s" % (out, start, end)
    cursor = add_month(cursor, 1)
    shells.append(command)

shells.sort(reverse=True)
with open("start_ingest_traffic.sh", "w") as w:
    for command in shells:
        w.write(command + "\n")

if __name__ == "__main__":
    pass

