#!/usr/bin/env python
# -*- coding: utf-8 -*-

import overpy, os, json

def parseData(dataList):
	if not dataList:
		return
	for date, streets in dataList.items():
		print(date, streets)


path = "results/"
for f in os.listdir(path):
	print("current file is: " + f)
	with open(os.path.join(path, f), "r") as fh:
		parseData(json.load(fh)["results"])

