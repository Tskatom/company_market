#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Construct the daily interaction network based on: mention, reply, retweet
by utilizing multuprocess. 
The input data are the daily users interactions.
For each date file, each record represent each user's mention/reply/retweet list
In the graph, user is the node and we will create a edge from user u to user v if u mention v or
retweet/reply v's post.
For each node, it has a attribute tweets number
for each edge, it has three atrributes "mention/retweet/reply" number
The input to the application is the folder of the daily actions files
The output is the daily interaction network
"""
__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import argparse
from multiprocessing import Process, Queue
from collections import Counter
import glob
import networkx as nx
import json

def build(task):
    """Build network based on task"""
    try:
        graph = nx.DiGraph()
        with open(task["file"]) as df:
            for line in df:
                action = json.loads(line)
                user = action["user"]
                actions = action["actions"]
                graph.add_node(user, tweets=actions["tweets"])

                #handle mentions
                men_counter = Counter(actions["mentions"])
                for t_user, num in men_counter.iteritems():
                    graph.add_edge(user, t_user, mentions=num)

                #handle retweet
                retweet_counter = Counter(actions["retweets"])
                for t_user, num in retweet_counter.iteritems():
                    graph.add_edge(user, t_user, retweets=num)

                #handle reply
                reply_counter = Counter(actions['replies'])
                for t_user, num in reply_counter.iteritems():
                    graph.add_edge(user, t_user, replies=num)
        nx.write_gexf(graph, task["output"])
        print 'Done[%s]' % task['file']
    except:
        print "Error:", task, sys.exc_info()[0], line

def worker(task_queue):
    for task in iter(task_queue.get, 'STOP'):
        build(task)

def create_task(args, task_queue):
    for f in glob.glob(os.path.join(args.in_folder, '*')):
        out_name = os.path.join(args.out_folder, os.path.basename(f) + ".gexf")
        task = {"file": f, "output": out_name}
        task_queue.put(task)

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in_folder', type=str,
            help='--the input actions folder')
    ap.add_argument('--out_folder', type=str,
            help='the output folder')
    ap.add_argument('--core', type=int,
            help='the number of cores to use')
    args = ap.parse_args()
    return args

def main():
    args = parse_args()
    task_queue = Queue()
    create_task(args, task_queue)

    for i in range(args.core):
        Process(target=worker, args=(task_queue,)).start()
        task_queue.put('STOP')  #add stop signal

if __name__ == "__main__":
    main()

