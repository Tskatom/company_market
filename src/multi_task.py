#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
from multiprocessing import Process, Queue
import json
from subprocess import call
import argparse
import glob
import urllib2
from goose import Goose
import nltk.data
import re
import urlparse
import jsonrpclib
from simplejson import loads
from dateutil import parser
from datetime import datetime
import networkx as nx
from nltk.tokenize import TreebankWordTokenizer
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn import metrics
from sklearn.svm import SVC
from sklearn.feature_selection import SelectPercentile, f_classif, SelectKBest, chi2
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize
import nltk.data
from collections import Counter
import pysolr


def worker(task_queue, result_queue=None):
    for task in iter(task_queue.get, 'STOP'):
        result = handler(task)
        if result_queue is not None:
            result_queue.put(result)
        
def handler(task):
    work_func = task["func"]
    result = work_func(task["params"])
    return result

def create_filtering_user_task(args, task_queue):
    folders = glob.glob(os.path.join(args.inFolder, "*"))
    for f in folders:
        param = {}
        param["companyFolder"] = f
        param["outFolder"] = args.outFolder
        task = {"params": param, "func": filtering_user}
        task_queue.put(task)
    task_count = len(folders)
    return task_count

def filtering_user(param):
    company_folder = param["companyFolder"]
    outFolder = param["outFolder"]
    files = glob.glob(os.path.join(company_folder, "*"))
    users = {}
    for f in files:
        with open(f) as tweet_f:
            for line in tweet_f:
                try:
                    tweet = json.loads(line)
                    user = tweet["user"]
                    #check whether the tweets containing URL or not
                    users.setdefault(user["id"], {"info": user, "urls": 0, "non_urls":0})
                    if "entities" in tweet and "urls" in tweet["entities"]:
                        if len(tweet["entities"]["urls"]) > 0:
                            users[user["id"]]["urls"] += 1
                        else:
                            users[user["id"]]["non_urls"] += 1
                    else:
                        users[user["id"]]["non_urls"] += 1
                except:
                    continue
    basename = os.path.basename(company_folder)
    outFile = os.path.join(outFolder, basename)
    with open(outFile, "w") as of:
        json.dump(users, of)
    print 'Finish %s' % company_folder

def create_import_tweets_task(args, task_queue):
    folders = glob.glob(os.path.join(args.inFolder, "*"))
    for f in folders:
        param = {}
        param["companyFolder"] = f
        task = {"params": param, "func": importTweet}
        task_queue.put(task)
    task_count = len(folders)
    return task_count

def importTweet(param):
    solr = pysolr.Solr("http://localhost:8983/solr", timeout=100)
    companyFolder = param["companyFolder"]
    companyName = os.path.basename(companyFolder)
    tweetFiles = glob.glob(os.path.join(companyFolder, "*"))
    docs = []
    for f in tweetFiles:
        with open(f) as tf:
            for line in tf:
                try:
                    tweet = json.loads(line)
                    doc = {}
                    doc["content"] = tweet['text']
                    doc["company"] = companyName
                    doc["author"] = tweet["user"]["name"]
                    doc["date"] = parser.parse(tweet["created_at"]).strftime("%Y-%m-%dT%H:%M:%SZ/DAY")
                    doc["terms"] = tweet["topsy"].get("terms", [])
                    doc["id"] = "%s_%d" % (companyName, tweet["id"])
                    docs.append(doc)
                except:
                    continue
    print "Documents: [%d]" % len(docs)
    solr.add(docs)
    #solr.optimize()
    solr.commit()
    print "Done with %s\n" % companyFolder


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--inFolder', type=str)
    ap.add_argument("--outFolder", type=str)
    ap.add_argument("--logFolder", type=str)
    ap.add_argument("--headerFile", type=str)
    ap.add_argument("--keywordsFile", type=str)
    ap.add_argument('--core', type=int)
    ap.add_argument('--task', type=str)
    ap.add_argument('--start', type=str)
    ap.add_argument('--end', type=str)
    ap.add_argument('--code', type=str)
    return ap.parse_args()


def main():
    args = parse_args()
    task_queue = Queue()
    result_queue = None

    if args.outFolder and not os.path.exists(args.outFolder):
        os.mkdir(args.outFolder)

    if args.logFolder and not os.path.exists(args.logFolder):
        os.system("mkdir -p %s" % args.logFolder)


    if args.task == "import":
        task_count = create_import_tweets_task(args, task_queue)
    elif args.task == "filtering_user":
        task_count = create_filtering_user_task(args, task_queue)

    for i in range(args.core):
        Process(target=worker, args=(task_queue,result_queue)).start()
        task_queue.put('STOP')
    
    #postprocess
    if result_queue:
        post_exe = call_back[args.task]
        post_exe(args, task_count, result_queue)

    print "------------------I am Done"


if __name__ == "__main__":
    main()

