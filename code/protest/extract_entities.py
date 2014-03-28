#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import argparse
import json

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fold', type=str, help="file folder")
    arg = ap.parse_args()
    return arg

def extract(folder):
    files = os.listdir(folder)
    types = ["hashtag", "urls", "media"]
    results = {field:{} for field in types}
    for f in files:
        f = os.path.join(folder, f)
        with open(f) as tf:
            for line in tf:
                tweet = json.loads(line)
                if "entities" not in tweet:
                    continue
                #handle hashtag
                for item in tweet["entities"]["hashtags"]:
                    hashtag = "#" + item["text"]
                    if hashtag in results["hashtag"]:
                        results["hashtag"][hashtag] += 1
                    else:
                        results["hashtag"][hashtag] = 1
                #handle urls
                for item in tweet["entities"]["urls"]:
                    url = item["expanded_url"]
                    if url in results["urls"]:
                        results["urls"][url] += 1
                    else:
                        results["urls"][url] = 1

                #handle medi
                if "media" not in tweet["entities"]:
                    continue
                for item in tweet["entities"]["media"]:
                    media_url = item["media_url"]
                    m_type = item["type"]
                    if media_url in results["media"]:
                        results["media"][media_url]["count"] += 1
                    else:
                        results["media"][media_url] = {"count": 1, "type": m_type}
    return results

def main():
    arg = parse_args()
    results = extract(arg.fold)
    json.dump(results, open("results.json", "w"))

if __name__ == "__main__":
    main()

