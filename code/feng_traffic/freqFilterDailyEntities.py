#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filter the entities less than some number
"""
__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
from multiprocessing import Process, Queue, freeze_support
import argparse
import logging
from datetime import datetime, timedelta
import json
from collections import Counter
import glob
from dateutil import parser

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fold', type=str,
            help='the tweets folder')
    ap.add_argument('--core', type=int,
            help='the core num')
    ap.add_argument('--out', type=str,
            help='output folder')
    ap.add_argument('--num', type=int,
            help='the threshold to filter the entities')
    arg = ap.parse_args()
    return arg

def worker(task_queue):
    for task in iter(task_queue.get, 'STOP'):
        filter_entities(task)

def normalize(u_word):
    return u_word.encode('utf-8')

def filter_entities(task):
    data_file = task['file']
    out_put = task["output"]
    ent_count = []
    threshold = task["threshold"]
    with open(data_file) as df:
        for line in df:
            entry = json.loads(line)
            ent_count.extend(entry["entities"]["hashtags"])
            ent_count.extend(entry["entities"]["urls"])
    ent_counter = Counter(ent_count)
    ent_final = {k:v for k,v in ent_counter.items() if v >= threshold}
    with open(data_file) as df, open(out_put, "w") as outf:
        for line in df:
            entry = json.loads(line)
            user = entry["user"]
            ents = []
            ents.extend([h for h in entry["entities"]["hashtags"] if h in ent_final])
            ents.extend([u for u in entry["entities"]["urls"] if u in ent_final])
            if len(ents) > 0:
                #ents = map(normalize, ents)
                ent_str = "%s|%s\n" % (user," ".join(ents))
                if isinstance(ent_str, unicode):
                    ent_str = ent_str.encode('utf-8')
                outf.write(ent_str)
    print "Done[%s]" % data_file
    

def create_task(args, task_queue):
    files = glob.glob(os.path.join(args.fold, "*"))
    for f in files:
        task = {}
        basename = "%s_%d"% (os.path.basename(f), args.num)
        task["file"] = f
        task["threshold"] = args.num
        task["output"] = os.path.join(args.out, basename)
        task_queue.put(task)

def main():
    args = parse_args()
    task_queue = Queue()

    create_task(args, task_queue)
    for i in range(args.core):
        Process(target=worker, args=(task_queue,)).start()
        task_queue.put('STOP')

if __name__ == "__main__":
    main()


