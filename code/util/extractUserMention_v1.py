#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
from multiprocessing import Process, Queue, freeze_support
import argparse
import logging
from datetime import datetime, timedelta
import json

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fold', type=str,
            help='the tweets folder')
    ap.add_argument('--core', type=int,
            help='the core num')
    ap.add_argument('--out', type=str,
            help='output')
    arg = ap.parse_args()
    return arg

def worker(task_queue, result_queue):
    for task in iter(task_queue.get, 'STOP'):
        result = get_mentions(task)
        result_queue.put(result)

def get_mentions(task):
    user = task["user"]
    files = task["files"]
    mentions = {}
    for f in files:
        with open(f) as tf:
            for line in tf:
                tweet = json.loads(line)
                author = tweet['user']['screen_name']
                for mention in tweet['entities']['user_mentions']:
                    mentioned = mention['screen_name']
                    if mentioned in mentions:
                        mentions[mentioned] += 1
                    else:
                        mentions[mentioned] = 1
    return {"user": user, "user_mentions": mentions}


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

def create_task(folder, task_queue):
    task_count = 0
    print folder
    subfolders = [os.path.join(folder, f) 
            for f in os.listdir(folder) if os.path.isdir(os.path.join(folder,f))]
    print subfolders
    for folder in subfolders:
        files = [f for f in read_folder(folder)]
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

    task_queue = Queue()
    result_queue = Queue()

    task_count = create_task(folder, task_queue)
    print task_count
    for i in range(core):
        Process(target=worker, args=(task_queue, result_queue)).start()

    #send stop signal
    for i in range(core):
        task_queue.put('STOP')

    #print result
    with open(output, "w") as wf:
        for i in range(task_count):
            mentions = result_queue.get()
            wf.write("%s\n" % json.dumps(mentions))


if __name__ == "__main__":
    main()


