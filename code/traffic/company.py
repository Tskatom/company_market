#!/usr/bin/python
#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib2

class Company(object):
	def __init__(self, url):
		self.url = url
		self.company_list = []
		self.rules = []
	def crawl(self):
		soup = BeautifulSoup(urllib2.urlopen(self.url).read())
		table = soup.find_all("table", class_="wikitable sortable")
		if not table:
			return
		for row in table[0].find_all("tr")[1:]:
			tds = [td for td in row.find_all("td")]
			symbol = tds[0].a.text
			name = tds[1].text
			gics_sec = tds[2].text
			gics_sub_sec = tds[3].text
			self.company_list.append([symbol, name, gics_sec, gics_sub_sec])

	def get_list(self):
		return self.company_list	

	def get_rules(self):
		return self.rules

	def create_rules(self, fined_list_file):
		with open(fined_list_file) as flf:
			for line in flf:
				infos = line.strip().split("|")
				name = infos[0]
				rule = "'%s' OR $%s" % (infos[1].strip(), name)
				self.rules.append("%s|%s" % (name, rule))

		
def main():
	url = "http://en.wikipedia.org/wiki/List_of_S%26P_400_companies"
	company = Company(url)
	company.crawl()
	company_list = company.get_list()
	out_file = "/home/weiwang/workspace/data/sp_400_list.txt"
	with open(out_file, "w") as ow:
		for com in company_list:
			ow.write("|".join(com) + "\n")

	fined_list_file = "/home/weiwang/workspace/data/fined_sp_400_list.txt"
	company.create_rules(fined_list_file)
	rules = company.get_rules()
	rule_file = "/home/weiwang/workspace/data/company_rules.txt"
	with open(rule_file, "w") as rw:
		for rule in rules:
			rw.write(rule + "\n")
			

if __name__ == "__main__":
	main()			
