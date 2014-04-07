#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import topsy
from multiprocessing import Process, Queue, freeze_support
import argparse
import logging
from datetime import datetime, timedelta
import config

logging.basicConfig(filename='topsyCraft.log', level=logging.INFO)

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rule', type=str,
            help='Query rule files line by line')
    ap.add_argument('--core', type=int,
            help='Num of cores to use')
    ap.add_argument('--out', type=str,
            help="output folder")
    ap.add_argument('--region',type=str,
            help="region code")
    ap.add_argument('--mintime', type=str,
            help='start time, format yyyy-mm-dd')
    ap.add_argument('--maxtime', type=str,
            help='end time, format yyyy-mm-dd')
    ap.add_argument('--split', action='store_true',
            help='whether split the output into subfolders')
    ap.add_argument('--tweet_types', type=str,
            help='result types:tweet, reply, retweet')
    arg = ap.parse_args()
    return arg

def create_task(start, end, rule, region, prefix, out_dir, queue, delta=24, tweet_types=None):
    """Create api task
    args:
        start:
            mintime to report
        end:
            maxtime to report
        rule:
            query terms
        prefix:
            prfix of the output file
        out_dir:
            output folder
        queue:
            the task queue
        delta:
            query interval, take hours as unit, does not split task when 
            delta=0
    """
    curr_day = datetime.now().strftime("%Y-%m-%d")
    if end > curr_day:
        end = curr_day
    start = "%s000000" % start.replace("-", "")
    end = "%s235959" % end.replace("-","")
    from_format = "%Y%m%d%H%M%S"
    to_format = "%s"
    cursor = start
    while cursor < end:
        cursor = (datetime.strptime(start, from_format) +
                timedelta(hours=delta)).strftime(from_format)
        if cursor > end or delta == 0:
            cursor = end
        param = {}
        param['limit'] = 20000
        param['sample'] = 100
        param['region'] = region
        include_enrichment_all = 1
        param['q'] = rule
        param['mintime'] = datetime.strptime(start, from_format).strftime(to_format)
        param['maxtime'] = datetime.strptime(cursor, from_format).strftime(to_format)
        param['tweet_types'] = tweet_types
        
        output = os.path.join(out_dir, "%s_%s_%s" % (prefix, 
            start, cursor))
        task = {"param": param, "output": output}
        queue.put(task)
        start = cursor

def bulkIngest(task):
    try:
        api = topsy.Api(api_key=config.APIKEY)
        param = task["param"]
        output = task["output"]
        result = api.bulkTweets(**param)
        with open(output, "w") as ow:
            for r in result:
                ow.write(r + "\n")
    except Exception as e:
        print "Error:[%s]" % sys.exc_info()[0]
        logging.warning("Error:[%s]" % sys.exc_info()[0]) 

def worker(task_que):
    for task in iter(task_que.get, 'STOP'):
        bulkIngest(task)

def main():
    arg = parse_args()
    task_queue = Queue()
    core_num = arg.core
    start = arg.mintime
    end = arg.maxtime
    outfolder = arg.out
    rule_file = arg.rule
    region = arg.region
    tweet_types = arg.tweet_types

    #create slaver process
    for i in range(core_num):
        Process(target=worker, args=(task_queue,)).start()

    #add task to queue
    with open(rule_file) as rf:
        for i, line in enumerate(rf):
            name, delta, rule = line.strip().split("|")
            out_dir = os.path.join(outfolder, str(i % 60))
            if not os.path.exists(out_dir):
                os.mkdir(out_dir)
            create_task(start, end, rule, region, name, out_dir, task_queue, float(delta), tweet_types)

    #send stop signal to slaver process
    for i in range(core_num):
        task_queue.put('STOP')


if __name__ == "__main__":
    sys.exit(main())
    

