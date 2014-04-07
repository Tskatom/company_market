#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import argparse
from multiprocessing import Process, Queue, freeze_support
import time
import json

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fold', type=str)
    ap.add_argument('--core', type=int)
    arg = ap.parse_args()
    return arg

def worker(in_que, out_que):
    for func, args in iter(in_que.get, 'STOP'):
        result = extract(func, args)
        out_que.put(result)

def extract(func, args):
    result = func(*args)
    return result

def get_user(file_name):
    result = {}
    with open(file_name) as tf:
        for line in tf:
            tweet = json.loads(line)
            name = tweet["user"]["screen_name"]
            result.setdefault(name, 0)
            result[name] += 1
    return result


def main():
    arg = parse_args()
    start = time.time()
    files = [os.path.join(arg.fold, f) for f in os.listdir(arg.fold)]
    #create Queue
    task_que = Queue()
    done_que = Queue()
    
    task = [(get_user, [f]) for f in files]
    for t in task:
        task_que.put(t)
    #start processes
    for i in range(arg.core):
        Process(target=worker, args=(task_que, done_que)).start()
    
    #compute the summary
    user_count = {}
    task_count = len(task)
    for i in range(task_count):
        result = done_que.get()
        for k, v in result.items():
            user_count.setdefault(k, 0)
            user_count[k] += v

    #dump the result
    with open("./user_count.txt", 'w') as usw:
        for name, count in user_count.items():
            usw.write("%s\t%d\n" % (name, count))

    #stop the child process
    for i in range(arg.core):
        task_que.put('STOP')

    print "Time elpased:[%d]" % (time.time() - start)

if __name__ == "__main__":
    main()

