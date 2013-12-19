#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import re
import logging
from disco.core import Job
import json


EXCEPT_CHAR = "@#$:/."


def tokenize(content):
    rule = '[^\w%s]+' % EXCEPT_CHAR
    content = content.lower()
    tokens = re.split(rule, content)
    return tokens


class TweetFilter(Job):
    @staticmethod
    def map(row, params):
        keywords = params["keyword"]
        try:
            tweet = json.loads(row)
            content = tweet["interaction"]["content"]
            tokens = tokenize(content)
            matched = []
            for token in tokens:
                #search in the keywords list
                if token in keywords:
                    company = keywords[token]
                    if company not in matched:
                        matched.append(company)
                        tweet["matched"] = {"company": company}
                        yield tweet, 1
        except Exception, e:
            logging.info("Exception: [%s]" % e)

if __name__ == "__main__":
    #from twitter_filter import TweetFilter
    from disco.core import result_iterator
    import sys
    from disco.ddfs import DDFS

    day = sys.argv[1]
    ddfs = DDFS()
    tags = ddfs.list("enriched:%s" % day)
    job_name = "Tweet_filter"
    params = {"venezuela": "venezuela"}
    inputs = [("tag://%s") % tag for tag in tags]
    job = TweetFilter().run(input=inputs,
                            partitions=10,
                            params=params,
                            name=job_name)
    result = job.wait(show=False)
    out_file = "filtered_tweet.txt"
    with open(out_file, "w") as ow:
        for k, v in result_iterator(result):
            ow.write(json.dumps(k) + "\n")
