#!/usr/bin/python
#-*- coding:utf8 -*-
"""
Analyze the clustering of the tweets
"""
__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import DBSCAN
import nltk
from glob import glob
import json
import unicodedata

class Cluster(object):
    """
    Clustering the tweets data
    """
    def __init__(self, min_sample, eps):
        self.min_sample = min_sample
        self.eps = eps
        self.vectorizer = CountVectorizer(min_df=1,
            stop_words='english', tokenizer=my_tokenizer)
        self.transfomer = TfidfTransformer()
        self.counts = None
        self.tfidf = None

    def load_data(self, data):
        """
        The data is a list of content
        """
        self.counts = self.vectorizer.fit_transform(data)
        self.tfidf = self.transfomer.fit_transform(self.counts.toarray())

    def run(self):
        """
        Run the clustering algorithm
        """
        dbscan = DBSCAN(eps=self.eps,
            min_samples=self.min_sample).fit(self.tfidf.toarray())
        labels = dbscan.labels_
        num_cluster_mem = len([label for label in labels if label != -1])
        cluster_index = [i for i, label in enumerate(labels) if label != -1]
        return (len(set(labels)) -
            1 if -1 in labels else 0), num_cluster_mem, cluster_index

def my_tokenizer(doc):
    """
    customized the tokenize method
    """
    tokens = []
    text = unicodedata.normalize('NFKC', doc).lower()
    tokens.extend([w for w in text.split()
        if w not in ['-', 'rt', '...', 'boyd', 'gaming'] +
        nltk.corpus.stopwords.words('english')])
    return tokens


def main():
    """
    main function
    """
    byd_files = sorted(glob("/home/weiwang/workspace/data/topsy_50/BYD*"))

    for byd_f in byd_files:
        contents = []
        with open(byd_f) as tweet_f:
            for line in tweet_f:
                tweet = json.loads(line)
                contents.append(tweet.get('text'))
        print "number of Documents: [%d]" % len(contents)
        if len(contents) == 0:
            continue
        cluster = Cluster(10, 0.3)
        cluster.load_data(contents)
        num, num_mems, cluster_index = cluster.run()
        if num > 0:
            print "Documents:[%s] Clusters:[%d] Members:[%d] in File [%s]" % (
                len(contents), num,
                num_mems, byd_f)
            for index in cluster_index:
                print contents[index]

if __name__ == "__main__":
    main()
