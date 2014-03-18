#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import urllib
import requests
import json

class TopsyError(Exception):
    """Base class for Topsy errors"""

    @property
    def message(self):
        """Returns the first argument used to construct the error"""
        return self.args[0]


class Api(object):
    """
    A python Interface for the Topsy API
    Including:
        bulkTweets
        locations
        relatedterms
    """

    def __init__(self, 
            base_url=None, 
            api_key=None):
        """ Instantiate a new Topsy.Api object
        Args:
            base_url:
                The base URL to use to contact to topsy API
            api_key:
                The API key used to invoke topsy API
        """

        if base_url is None:
            self.base_url = "http://api.topsy.com/v2/"
        else:
            self.base_url = base_url

        if api_key is None:
            print >> sys.stderr, 'Topsy requires API keyfor API call'
            raise TopsyError("The Topsy API need a API key.")
        else:
            self.api_key = api_key

    def _request(self, url):
        try:
            print url
            r = requests.get(url)
        except Exception as e:
            raise TopsyError('Failed to handle the topsy api request[%s]' % url)
        else:
            q_status = r.iter_lines().next()
            if 'error' in json.loads(q_status):
                raise TopsyError(q_status)
            return r

    def _buildUrl(self, path, **kwargs):
        """Build the url, path should not start with /"""
        url = "%s%s?" % (self.base_url, path)
        params = {k:v for k, v in kwargs.items() if v is not None}
        return "%s%s" % (url, urllib.urlencode(params))

    def bulkTweets(self, 
            q=None,
            limit=10,
            include_enrichment_all=None,
            sample=10,
            mintime=None,
            maxtime=None,
            region=None,
            latlong=None,
            allow_lang=None,
            infonly=None,
            tweet_types=None
            ):
        """
        Provides a large set of tweets that match the specified query and filter parameters.
        The maximum number of items returned per query is 20,000
        Args:
            q:
                The search terms or rule
            limit:
                The maximum bumber of results returned
            include_enrichment_all:
                Include Topsy enrichment fields
            sample:
                When set to 1, only 1% subsample of the result set is returned.
            mintime:
                starttime for the report in Unix timestamp
            maxtime:
                endtime for the report in Unix timestamp
            region:
                show results for the specified locations only. A valid region integer ID
                must be used. Region IDs can be found using /location resource call
            latlong:
                show results from tweets that are geotagged with lat/long only, Enabled when 
                latlong=1, default=0
            allow_lang:
                show results in the specified language. currently support 'en'(English), 
                'ja'(Japanese), 'ko'(Korean), 'ru'(Russian), 'es'(Spanish), 'fr'(French), 
                'de'(German), 'pt'(Portuguese), 'tr'(Turkish)
            infonly:
                show results from influential users only. Enabled when infonly=1, default is 0
            tweets_types:
                show results with specified tweets type, currently support 'tweet', 'reply',
                'retweet'
        """
        url = self._buildUrl('content/bulktweets.json', 
                q=q,
                limit=limit,
                include_enrichment_all=include_enrichment_all,
                sample=sample,
                mintime=mintime,
                maxtime=maxtime,
                region=region,
                latlong=latlong,
                allow_lang=allow_lang,
                infonly=infonly,
                tweet_types=tweet_types,
                apikey=self.api_key)
        response = self._request(url)
        return response.iter_lines()

if __name__ == "__main__":
    pass

