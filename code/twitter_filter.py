#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import re
import logging
from disco.core import Job
import json
import worker

EXCEPT_CHAR = "@#$:/.-&"


def tokenize(content):
    rule = '[^\w%s]+' % EXCEPT_CHAR
    content = content.lower()
    tokens = re.split(rule, content)
    return tokens


def normalize_str(s):
    try:
        if s == None:
            s = ""
        if isinstance(s, str):
            return unidecode(s.decode('utf-8').strip()).lower()
    except UnicodeDecodeError:
        return s
    return unidecode(unicode(s).strip()).lower()

class TweetFilter(Job):
    @staticmethod
    def map(entry, params):
        keywords = params
        try:
            t, tweets = entry
            for tweet in json.loads(tweets):
                content = tweet["interaction"]["content"]
                tokens = tokenize(content)
                matched = []
                logging.info("tokens: %s" % tokens)

                for keyword in keywords:
                    find = None
                    if len(keyword.split(" ")) > 1:
                        #match the sentence
                        find = re.search(r'\b(%s)\b' % keyword, content, re.IGNORECASE)
                    else:
                        if keyword in tokens:
                            find = keyword
                    if find:
                        company = keywords[keyword]
                        if company not in matched:
                            matched.append(company)
                            tweet["matched"] = {"company": company, "matched": keyword}
                            yield company, json.dumps(tweet, encoding='utf8', ensure_ascii=False).encode('utf8')
        except Exception, e:
            print "Exception: [%s]" % e

    @staticmethod
    def map_reader(stream, size, url, params):
        """Input stream for Twitter data"""
        import struct, cStringIO, zlib
        data_format = "<qQIQQQ"
        data_length = struct.calcsize(data_format)
        offset = 0
        exp_value = "3mb3rs"
        while True:
            header = stream.read(len(exp_value))
            if not header:
                return
                raise DataError("Not a valid twitter data chunk at %s size=%d" % (header, size), url)

            if header != exp_value:
                raise DataError("Not a valid twitter data chunk at %s" % url, url)

            try:
                time, hunk_size, checksum, res1, res2, res3 =\
                    struct.unpack(data_format, stream.read(data_length))
            except:
                raise DataError("Truncated data at %d bytes" % offset, url)

            if not hunk_size:
                return

            hunk = stream.read(hunk_size)
            data = ''
            try:
                data = zlib.decompress(hunk)
                if checksum != (zlib.crc32(data) & 0xFFFFFFFF):
                    raise ValueError("Checksum does not match")
            except (ValueError, zlib.error), e:
                raise DataError("Corrupted data between bytes %d-%d: %s" % (offset, offset + hunk_size, e), url)
            offset += hunk_size + data_length
            yield time, data


if __name__ == "__main__":
    from twitter_filter import TweetFilter
    from disco.core import result_iterator
    from disco.ddfs import DDFS
    import sys

    day = sys.argv[1]
    ddfs = DDFS()
    tags = ddfs.list("enriched:%s" % day)
    job_name = "Tweet_filter"
    params = {"venezuela avanza": "venezuela"}
    inputs = [("tag://%s") % tag for tag in tags[0:2]]
    job = TweetFilter().run(input=inputs,
                            partitions=10,
                            params=params,
                            name=job_name)
    result = job.wait(show=False)
    out_file = "filtered_tweet_3.txt"
    with open(out_file, "w") as ow:
        for k, v in result_iterator(result):
            ow.write(v + "\n")
