#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
from multiprocessing import Process, Queue
import argparse
from operator import itemgetter
import json

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fold', type=str,
            help='actions folder')
    ap.add_argument('--out', type=str,
            help='action count file')
    ap.add_argument('--core', type=int,
            default=40, help='number of process')
    arg = ap.parse_args()
    return arg

def worker(in_queue, out_queue):
    for task in iter(in_queue.get, 'STOP'):
        result = count_action(task)
        out_queue.put(result)

def count_action(task):
    result = {"date":task["date"], "retweets":0, "mentions":0,
            "tweets":0, "replies":0}
    with open(task["file"]) as tf:
        for line in tf:
            data = json.loads(line)
            result["tweets"] += data["actions"]["tweets"]
            result["mentions"] += len(data["actions"]["mentions"])
            result["retweets"] += len(data["actions"]["retweets"])
            result["replies"] += len(data["actions"]["replies"])
    print "Done %s" % task["date"]
    return result

def create_tasks(infold, task_queue):
    task_count = 0
    for f in os.listdir(infold):
        task = {"date": f, "file": os.path.join(infold, f)}
        task_queue.put(task)
        task_count += 1
    return task_count

def output(task_count, out_queue, out_file):
    results = sorted([out_queue.get() for i in range(task_count)], key=itemgetter("date"))
    with open(out_file, "w") as of:
        of.write("%s\t%s\t%s\t%s\t%s\n" % ("date", "tweets", "mentions", "retweets", "replies"))
        
        for result in results:
            of.write("%s\t%s\t%s\t%s\t%s\n" %
                    (result["date"], result["tweets"], result["mentions"], 
                        result["retweets"], result["replies"]))


def main():
    arg = parse_args()
    core = arg.core
    out = arg.out
    fold = arg.fold
    task_queue = Queue()
    result_queue = Queue()
    
    task_count = create_tasks(fold, task_queue)
    print "Task Number: %d" % task_count

    #create Process
    for i in range(core):
        Process(target=worker, args=(task_queue, result_queue)).start()
        task_queue.put('STOP')
    output(task_count, result_queue, out)

if __name__ == "__main__":
    main()

