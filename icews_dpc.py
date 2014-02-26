#/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import pandas as pd
from datetime import datetime, timedelta
from etool import message, args
import json
import os
import boto
import sys


def parse_args():
    ap = args.get_parser()
    ap.add_argument("--create", action='store_true', help="flag representing make prediction")
    ap.add_argument("--update", action='store_true', help="flag representing update prediction")
    ap.add_argument("--date", type=str, help="date YYYY-mm-dd to predict or update")
    ap.add_argument("--file", type=str, help="warning file")
    ap.add_argument("--surr", type=str, help="surrogate file")
    ap.add_argument("--out", type=str, default="." + os.sep, help="the output folder")
    ap.add_argument("--dpc", action='store_true', help="make dpc prediction")
    ap.add_argument("--icews", action='store_true', help="make the icews prediction")
    arg = ap.parse_args()
    return arg

class Icews:
    def __init__(self, arg):
        self.arg = arg
        self.ws = json.load(open(self.arg.file))
        self.event_type = "06"

    def run(self):
        if self.arg.create:
            self.create_warning()

        if self.arg.update:
            self.update_warning()

    def create_warning(self):
        warning_file = os.path.join(self.arg.out, "ICEWS_warnings_%s" % datetime.now().strftime("%Y-%m-%dT%H-%M-%S"))
        surrogate_file = os.path.join(self.arg.out, "ICEWS_surrogates_%s" % datetime.now().strftime("%Y-%m-%dT%H-%M-%S"))
        #load the surrogate file
        surro_fr = pd.DataFrame.from_csv(self.arg.surr)
        cols = list(surro_fr.columns)
        with open(warning_file, "w") as wf, open(surrogate_file, "w") as sf:
            for country, count in self.ws.iteritems():
                eventDate = self.arg.date
                #get this Mon and last Tue
                end = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                start = (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d")
                count_warning = {}
                #cook the surrogate date
                surrogate = {"day": end, "colomuns": cols, "values":list(surro_fr.ix[country]), "country": country}
                surrogate = message.add_embers_ids(surrogate)

                count_warning["derivedFrom"] = {
                "source": "ICEWS event",
                "start": start,
                "end": end,
                "derivedIds": [surrogate["embersId"]]
                }

                count_warning["confidence"] = 1.0
                count_warning["comments"] = "ICEWS warning for predicting weekly protest counts"
                count_warning["eventType"] = self.event_type

                count_warning["eventDate"] = eventDate
                #check whether the eventDate is wed
                if datetime.strptime(eventDate, "%Y-%m-%d").weekday() != 2:
                    print "%s Not Wed" % eventDate
                    break
                count_warning["warningUpdate"] = None
                count_warning["version"] = "1.0.0"
                count_warning["location"] = [country, "-", "-"]
                count_warning["date"] = datetime.utcnow().isoformat()
                count_warning["model"] = "ICEWS Protest Model"
                count_warning["population"] = count
                count_warning["confidenceIsProbability"] = False
                count_warning = message.add_embers_ids(count_warning)

                wf.write(json.dumps(count_warning) + "\n")
                sf.write(json.dumps(surrogate) + "\n")

    def update_warning(self):
        conn = boto.connect_sdb()
        domain = conn.lookup('warnings')

        warning_file = os.path.join(self.arg.out, "ICEWS_warnings_%s" % datetime.now().strftime("%Y-%m-%dT%H-%M-%S"))
        surrogate_file = os.path.join(self.arg.out, "ICEWS_surrogates_%s" % datetime.now().strftime("%Y-%m-%dT%H-%M-%S"))

        surro_fr = pd.DataFrame.from_csv(self.arg.surr)
        cols = list(surro_fr.columns)

        with open(warning_file, "w") as wf, open(surrogate_file, "w") as sf:
            for country, count in self.ws.iteritems():
                eventDate = self.arg.date
                #get this Mon and last Tue
                end = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                start = (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d")
                count_warning = {}
                #cook the surrogate date
                surrogate = {"day": end, "colomuns": cols, "values":list(surro_fr.ix[country]), "country": country}
                surrogate = message.add_embers_ids(surrogate)

                count_warning["derivedFrom"] = {
                "source": "ICEWS event",
                "start": start,
                "end": end,
                "derivedIds": [surrogate["embersId"]]
                }



                #query the previous embers_id
                location = '["%s", "-", "-"]' % country
                query_sql = "select date, embersId from warnings where eventType='%s' and eventDate='%s' and location='%s' " % (self.event_type, eventDate, location)
                rs = domain.select(query_sql)
                previous_warnings = []
                for r in rs:
                    if "mitreMessage" in r:
                        previous_warnings.append((r['date'], r['embersId']))
                previous_warnings.sort(key=lambda x:x[0], reverse=True)
                previous_embers_id = previous_warnings[0][1]

                count_warning["confidence"] = 1.0
                count_warning["comments"] = "ICEWS weekly protest count warning updated for [%s] " % previous_embers_id
                count_warning["eventType"] = self.event_type
                count_warning["eventDate"] = eventDate
                count_warning["warningUpdate"] = previous_embers_id
                count_warning["version"] = "1.0.0"
                count_warning["location"] = [country, "-", "-"]
                count_warning["date"] = datetime.utcnow().isoformat()
                count_warning["model"] = "ICEWS Protest Model"
                count_warning["population"] = count
                count_warning["confidenceIsProbability"] = False
                count_warning = message.add_embers_ids(count_warning)

                wf.write(json.dumps(count_warning) + "\n")
                sf.write(json.dumps(surrogate) + "\n")

class DPC:
    def __init__(self, arg):
        self.arg = arg
        self.ws = json.load(open(self.arg.file))
        self.event_type = "05"

    def run(self):
        if self.arg.create:
            self.create_warning()

        if self.arg.update:
            self.update_warning()

    def create_warning(self):
        warning_file = os.path.join(self.arg.out, "DPC_warnings_%s" % datetime.now().strftime("%Y-%m-%dT%H-%M-%S"))
        surrogate_file = os.path.join(self.arg.out, "DPC_surrogates_%s" % datetime.now().strftime("%Y-%m-%dT%H-%M-%S"))

        surro_fr = pd.DataFrame.from_csv(self.arg.surr)
        cols = list(surro_fr.columns)

        with open(warning_file, "w") as wf, open(surrogate_file, "w") as sf:
            for country, probability in self.ws.iteritems():
                dpc_warning = {}
                #construct surrogate message
                eventDate = self.arg.date
                #get this Mon and last Tue
                end = datetime.now().strftime("%Y-%m-%d")
                start = (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d")
                #cook the surrogate date
                surrogate = {"day": end, "colomuns": cols, "values":list(surro_fr.ix[country]), "country": country}
                surrogate = message.add_embers_ids(surrogate)

                dpc_warning["confidence"] = 1.0
                dpc_warning["comments"] = "DPC warnings from DPC prediction Model"
                dpc_warning["eventType"] = self.event_type
                dpc_warning["eventDate"] = eventDate
                dpc_warning["warningUpdate"] = None
                dpc_warning["version"] = "1.0.0"
                dpc_warning["location"] = [country, "-", "-"]
                dpc_warning["date"] = datetime.utcnow().isoformat()
                dpc_warning["model"] = "DPC prediction Model"
                dpc_warning["population"] = probability
                dpc_warning["confidenceIsProbability"] = False
                dpc_warning = message.add_embers_ids(dpc_warning)

                wf.write(json.dumps(dpc_warning) + "\n")
                sf.write(json.dumps(surrogate) + "\n")

    def update_warning(self):
        conn = boto.connect_sdb()
        domain = conn.lookup('warnings')
        warning_file = os.path.join(self.arg.out, "DPC_warnings_%s" % datetime.now().strftime("%Y-%m-%dT%H-%M-%S"))
        surrogate_file = os.path.join(self.arg.out, "DPC_surrogates_%s" % datetime.now().strftime("%Y-%m-%dT%H-%M-%S"))

        surro_fr = pd.DataFrame.from_csv(self.arg.surr)
        cols = list(surro_fr.columns)

        with open(warning_file, "w") as wf, open(surrogate_file, "w") as sf:
            for country, probability in self.ws.iteritems():
                dpc_warning = {}
                #construct surrogate message
                eventDate = self.arg.date
                #get this Mon and last Tue
                end = datetime.now().strftime("%Y-%m-%d")
                start = (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d")
                #cook the surrogate date
                surrogate = {"day": end, "colomuns": cols, "values":list(surro_fr.ix[country]), "country": country}
                surrogate = message.add_embers_ids(surrogate)

                #query the previous embers_id
                location = '["%s", "-", "-"]' % country
                query_sql = "select date, embersId from warnings where eventType='%s' and eventDate='%s' and location='%s' " % (self.event_type, eventDate, location)
                rs = domain.select(query_sql)
                #query the previous embers_id
                location = '["%s", "-", "-"]' % country
                query_sql = "select date, embersId from warnings where eventType='%s' and eventDate='%s' and location='%s' " % (self.event_type, eventDate, location)
                rs = domain.select(query_sql)
                previous_warnings = []
                for r in rs:
                    if "mitreMessage" in r:
                        previous_warnings.append((r['date'], r['embersId']))
                previous_warnings.sort(key=lambda x:x[0], reverse=True)
                previous_embers_id = previous_warnings[0][1]

                dpc_warning["confidence"] = 1.0
                dpc_warning["comments"] = "Update DPC warning for [%s] from DPC prediction Model" % previous_embers_id
                dpc_warning["eventType"] = self.event_type
                dpc_warning["eventDate"] = eventDate
                dpc_warning["warningUpdate"] = previous_embers_id
                dpc_warning["version"] = "1.0.0"
                dpc_warning["location"] = [country, "-", "-"]
                dpc_warning["date"] = datetime.utcnow().isoformat()
                dpc_warning["model"] = "DPC prediction Model"
                dpc_warning["population"] = probability
                dpc_warning["confidenceIsProbability"] = False
                dpc_warning = message.add_embers_ids(dpc_warning)

                print dpc_warning
                wf.write(json.dumps(dpc_warning) + "\n")
                sf.write(json.dumps(surrogate) + "\n")
        pass


def main():
    arg = parse_args()

    print arg
    if not arg.create and not arg.update:
        print "Please input either --create or --update"
        sys.exit()

    if not arg.icews and not arg.dpc:
        print "Please input either --dpc or --icews"
        sys.exit()

    if arg.create and arg.update:
        print "You can only input either --create or --update"
        sys.exit()

    if arg.dpc and arg.icews:
        print "You can only input either --dpc or --icews"
        sys.exit()

    assert arg.date, "Please input a eventDate"
    assert arg.file, "Please input a warning file"
    assert arg.surr, "Please input a surrogate file"

    if arg.icews:
        #check whether the eventDate is wed
        if datetime.strptime(arg.date, "%Y-%m-%d").weekday() != 2:

            print "%s Not Wed" % arg.date
            sys.exit()
        icews = Icews(arg)
        icews.run()
    if arg.dpc:
        #check whether the date is in the middle of the month
        if arg.date[-2:] != '15':
            print "eventDate for DPC must be yyyy-mm-15"
            sys.exit()

        dpc = DPC(arg)
        dpc.run()

if __name__ == "__main__":
    sys.exit(main())



