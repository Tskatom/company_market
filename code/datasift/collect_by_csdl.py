#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Query the historic tweets through datasift

"""
__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import datasift
import argparse
import config
from datetime import datetime

class Env:
    def __init__(self, args):
        self._user = datasift.User(config.username, config.api_key)
        self.histories = []
        informat = "%Y%m%d%H%M%S"
        outformat = "%s"
        self.start = datetime.strptime(args.start, informat).strftime(outformat)
        self.end = datetime.strptime(args.end, informat).strftime(outformat)
        self.csdl_file = args.csdl_file
        self.name = args.name
        self.sample = args.sample
        self.source = args.source

    def create_historic(self):
        csdl = open(self.csdl_file).read()
        definition = self._user.create_definition(csdl)
        historic = definition.create_historic(self.start,
                                              self.end,
                                              self.source.split(","),
                                              self.sample,
                                              self.name)

        self.histories.append(historic)
        self.display_historic_details(historic)
        return historic

    def consume(self, playback_id=None):
        if playback_id:
            historic = self._user.get_historic(playback_id)
        else:
            historic = self.create_historic()

        self.display_historic_details(historic)

        params = "method=POST delivery_frequency=10 url=http://38.68.232.222:8787 auth.type=none"
        output_type= "http"
        push_def = self._user.create_push_definition()
        push_def.set_output_type(output_type)
        for arg in params.split(" "):
            key, val = arg.split("=")
            push_def.set_output_param(key, val)

        sub = push_def.subscribe_historic(historic, self.name)
        historic.start()


    def display_historic_details(self, historic):
        print 'Playback ID:  ', historic.get_hash()
        print 'Stream hash:  ', historic.get_stream_hash()
        print 'Name:         ', historic.get_name()
        print 'Start time:   ', historic.get_start_date()
        print 'End time:     ', historic.get_end_date()
        print 'Sources:      ', historic.get_sources();
        print 'Created at:   ', historic.get_created_at()
        print 'Status:       ', historic.get_status()
        print 'Progress:     ', '%d%%' % (historic.get_progress())


    def start(self):
        for historic in self.histories:
            historic.start()

    def query(self, playback_id):
        historic = self._user.get_historic(playback_id)
        self.display_historic_details(historic)


def parse_args():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('-s', dest='start', type=str,
                        help='Start time of query')
    parser.add_argument('-e', dest='end', type=str,
                        help='End time of query')
    parser.add_argument('-n', dest="name", type=str,
                        help='name of the stream')
    parser.add_argument('-sp', dest="sample", default='10',
                        type=str, help="sample percentage")
    parser.add_argument('-so', dest="source", type=str,
                        default="twitter")
    parser.add_argument('-csdl', dest='csdl_file',
                        type=str, help='the path of csdl file')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    print args
    env = Env(args)
    #playback_id = "8e0d19495ba27a7a5bef"
    #playback_id = "9c71c58f1b365dde65e0"
    #env.query(playback_id)
    env.consume()
    #env.create_historic()

if __name__ == "__main__":
    main()

