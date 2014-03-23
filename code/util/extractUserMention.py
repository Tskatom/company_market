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

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fold', type=str,
            help='the tweets folder')
    arg = ap.parse_args()
    return arg

def worker(task_queue, result_queue):
    for task in iter(task_queue.get, 'STOP'):
        pass

def read_folder(folder):
    for f in os.listdir(folder):
        f = os.path.join(folder, f)
        if os.path.isdir(f):
            for inner_f in read_folder(f):
                yield inner_f
        else:
            yield f


if __name__ == "__main__":
    pass

