#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
from datetime import timedelta, datetime
import calendar

start_month = "2011-06"
end_month = "2014-02"

def add_month(year_month, num):
    year, month = map(int, year_month.split("-"))
    month = month - 1 + num
    year = year + month / 12

    month = month % 12 + 1
    return "%d-%02d" % (year, month)
shells = []
cursor = start_month
out_dir = sys.argv[1]
shell_name = sys.argv[2]

while cursor <= end_month:
    year, month = map(int, cursor.split("-"))
    start = "%s-%s" % (cursor, "01")
    end = "%s-%d" %(cursor, calendar.monthrange(year, month)[1])

    out = os.path.join(out_dir, cursor.replace("-", ""))
    command = "nohup python multithread_topsy.py %s $1 %s %s &" % (out, start, end)
    cursor = add_month(cursor, 1)
    shells.append(command)

shells.sort(reverse=True)
with open(shell_name, "w") as w:
    for command in shells:
        w.write(command + "\n")

if __name__ == "__main__":
    pass

