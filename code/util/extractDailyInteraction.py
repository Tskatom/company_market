#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
extract the interaction between users in the daily tweet network,
we extract following actions:
    tweets sent
    mentions
    replies
    retweents
for each day, we will output a file in which each line is for a user
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
from dateutil import parser

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fold', type=str,
            help='the tweets folder')
    ap.add_argument('--core', type=int,
            help='the core num')
    ap.add_argument('--out', type=str,
            help='output folder')
    ap.add_argument('--start', type=str,
            help='the mini time to handle the files')
    arg = ap.parse_args()
    return arg

def worker(task_queue, result_queue):
    for task in iter(task_queue.get, 'STOP'):
        result = extract_actions(task)
        result_queue.put(result)

def extract_actions(task):
    user = task["user"]
    files = task["files"]
    actions = {}
    for f in files:
        with open(f) as tf:
            for line in tf:
                try:
                    tweet = json.loads(line)
                    day = parser.parse(tweet['created_at']).strftime("%Y-%m-%d")
                    actions.setdefault(day,{"tweets":0, 
                        "mentions":[],
                        "replies":[],
                        "retweets":[]})
                    actions[day]["tweets"] += 1
                    #extract mention info
                    mention = [m["screen_name"] for m in tweet["entities"]["user_mentions"]]
                    actions[day]["mentions"].extend(mention)
                    #add reply infomation
                    if tweet["in_reply_to_screen_name"]:
                        actions[day]['replies'].append(tweet['in_reply_to_screen_name'])
                    #check retweet information
                    if "retweeted_status" in tweet:
                        ori_user = tweet['retweeted_status']['user']['screen_name']
                        actions[day]['retweets'].append(ori_user)
                except:
                    print 'error[%s]' % sys.exc_info()[0]
    return {"user": user, "actions": actions}


def read_folder(folder):
    for f in os.listdir(folder):
        f = os.path.join(folder, f)
        if os.path.isdir(f):
            for inner_f in read_folder(f):
                yield inner_f
        else:
            yield f

def merge_files(files):
    files.sort()
    p_name = None
    p_file = None
    p_sets = []
    for f in files:
        name = f.split('/')[-1][0:-30]
        if name != p_name and p_name is not None:
            yield (p_name, p_sets)
            p_sets = []
            p_name = None
        p_name = name
        p_sets.append(f)
    yield (p_name, p_sets)

def create_task(folder, task_queue, start=None):
    task_count = 0
    print folder
    subfolders = [os.path.join(folder, f) 
            for f in os.listdir(folder) if os.path.isdir(os.path.join(folder,f))]
    print subfolders
    for folder in subfolders:
        if start is None:
            files = [f for f in read_folder(folder)]
        else:
            files = [f for f in read_folder(folder) if f.find(start) != -1]
        for name, f_set in merge_files(files):
            task = {"user": name, "files":f_set}
            task_queue.put(task)
            task_count += 1
    return task_count

def main():
    arg = parse_args()
    folder = arg.fold
    core = arg.core
    output = arg.out
    start = arg.start
    if start:
        start = start.replace('-', '') + '000000'

    task_queue = Queue()
    result_queue = Queue()

    task_count = create_task(folder, task_queue, start)
    print task_count
    for i in range(core):
        Process(target=worker, args=(task_queue, result_queue)).start()

    #send stop signal
    for i in range(core):
        task_queue.put('STOP')

    #print result
    out_files = {}
    for i in range(task_count):
        actions = result_queue.get()
        user = actions["user"]
        for day in actions["actions"]:
            if day not in out_files:
                out_files[day] = open(os.path.join(output, day), "w")
            out_files[day].write(json.dumps({"user": user, "actions": actions["actions"][day]}) + "\n")
    for day in out_files:
        out_files[day].flush()
        out_files[day].close()


if __name__ == "__main__":
    main()


