#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
from multiprocessing import Queue, Process
import networkx as nx
import argparse
import glob
import json

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--core', type=int, 
            help='number of core to use')
    ap.add_argument('--input', type=str,
            help='the input network file folder')
    ap.add_argument('--out', type=str,
            help='the output folder')
    return ap.parse_args()

def strong_components(task):
    """
    args:
        task    format{'file': task_file, 'output': output_fle}
    return:
        null    the scc result will be writen into output_file
    """
    net_file = task['file']
    output = task['output']

    g = nx.read_gexf(net_file)
    scc = nx.strongly_connected_components(g)
    json.dump(scc, open(output,'w'))
    print "Done[%s]" % task['file']

def worker(task_que):
    for task in iter(task_que.get, 'STOP'):
        strong_components(task)

def create_scc_tasks(args, task_que):
    files = glob.glob(os.path.join(args.input, '*'))
    if not os.path.exists(args.out):
        os.mkdir(args.out)

    for f in files:
        task = {}
        output = os.path.basename(f).split('.')[0] + ".scc"
        task['file'] = f
        task['output'] = os.path.join(args.out, output)
        task_que.put(task)

def main():
    args = parse_args()
    task_queue = Queue()
    create_scc_tasks(args, task_queue)
    #create processes
    for i in range(args.core):
        Process(target=worker, args=(task_queue,)).start()
        task_queue.put('STOP')


if __name__ == "__main__":
    main()

