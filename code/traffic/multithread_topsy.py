#!/usr/bin/python
# -*- coding:utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"


_APIKEY = '09C43A9B270A470B8EB8F2946A9369F3'
_URL = 'http://api.topsy.com/v2/content/bulktweets.json?'


import urllib2
import urllib
import logging
import os
import sys
from datetime import datetime, timedelta
import Queue
from threading import Thread
from subprocess import call
import time

logging.basicConfig(filename='multithread_topsy.log', level=logging.INFO)


class Spider(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            try:
                task = self.queue.get()
                url = task["url"]
                output = task["output"]
                start_task = time.time()
                print "Starting ingest [%s]" % output
                result = urllib2.urlopen(url)
                block_size = 8192
                with open(output, "w") as ow:
                    while True:
                        buffer = result.read(block_size)
                        if not buffer:
                            break
                        ow.write(buffer)
            except:
                logging.warning("Error:[%s]" % sys.exc_info()[0])
                #clean the output file
                if output:
                    command = "rm -rf %s" % output
                    call(command, shell=True)
            finally:
                self.queue.task_done()
                end_task = time.time()
                print "End ingest [%s], Time elpased [%f]" % (output,
                                                              end_task -
                                                              start_task)


def create_url(start, end, rule):
    param = {}
    param["apikey"] = _APIKEY
    param["limit"] = 20000
    param["sample"] = 100
    param["include_metrics"] = 1
    param["region"] = "225,223"
    param["q"] = rule

    informat = "%Y%m%d%H%M%S"
    outformat = "%s"
    start_epco = datetime.strptime(start, informat).strftime(outformat)
    end_epco = datetime.strptime(end, informat).strftime(outformat)

    param["mintime"] = start_epco
    param["maxtime"] = end_epco

    target_url = _URL + urllib.urlencode(param)
    return target_url


def create_task(start, end, rule, company, out_dir, queue, delta=24):
    """
        start, end: yyyy-mm-dd
        rule: query string like "'3D Systems' OR $DDD"
        company: the stock symbol
        out_dir: the output directory
        queue: the queue used to schedule the task
        delta: take hours as unit
    """
    start = "%s000000" % start.replace("-", "")
    end = "%s235959" % end.replace("-", "")
    cursor = start

    while cursor < end:
        cursor = (datetime.strptime(start, "%Y%m%d%H%M%S") +
                  timedelta(hours=delta)).strftime("%Y%m%d%H%M%S")
        if cursor > end:
            cursor = end
        url = create_url(start, cursor, rule)
        output = os.path.join(out_dir, "%s_%s_%s" % (company, start, cursor))
        task = {"url": url, "output": output}
        queue.put(task)
        start = cursor


def main():
    queue = Queue.Queue()
    out_dir = sys.argv[1]
    rule_files = sys.argv[2]
    start = sys.argv[3]
    end = sys.argv[4]

    if len(sys.argv) > 5:
        num_threads = int(sys.argv[5])
    else:
        num_threads = 30
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    #out_dir = "/home/weiwang/workspace/data"
    #rule_files = "/home/weiwang/workspace/data/company_rules.txt"
    #start = "2014-01-01"
    #end = "2014-01-31"
    #create threads
    for i in range(num_threads):
        t = Spider(queue)
        t.setDaemon(True)
        t.start()

    #push tasks to the queue
    with open(rule_files) as rf:
        for line in rf:
            name, delta, rule = line.strip().split("|")
            create_task(start, end, rule, name, out_dir, queue, int(delta))

    queue.join()

if __name__ == "__main__":
    main()
