#!/usr/bin/env python
import urllib.request
import urllib.error
from io import BytesIO
import json
import os
import re
import time

from lxml import etree

urls = json.load(open("pressemitteilungen.json"))

result = {}

for url in urls:
    print(url["url"])
    data = None
    i = 3
    while data is None and i > 0:
        try:
            data = urllib.request.urlopen(url["url"]).read()
        except urllib.error.URLError as e:
            time.sleep(1)
            print(e)
        i -= 1

    if data is None and i == 0:
        print("Error: skipping")
        continue

    parser = etree.HTMLParser()

    tree = etree.parse(BytesIO(data), parser)

    regex_date = re.compile("^\w+, (?P<day>\d+)\.(?P<month>\d+)(\.(?P<year>\d+))?")
    regex_street = re.compile("^\w+")

    cur_date = None
    cur_ym = None
    for elem in tree.xpath("//div[@id='col2_content']/div[2]"):
        for elem2 in elem.xpath("descendant-or-self::*/text()"):
            m = regex_date.match(elem2)
            if m:
                month = m.group("month")
                year = m.group("year")
                if year is None:
                    url_parts = url["url"].rsplit("/", 2)
                    if len(url_parts) > 2:
                        year = url_parts[1]
                        if int(month) == 1:
                            year = int(year) + 1

                s = "%s-%s-%s" % (year, month, m.group("day"))
                ym = "%s-%s" % (year, month)
                if ym not in result:
                    result[ym] = {
                        "url": url["url"],
                        "results": {},
                    }
                if s not in result[ym]["results"]:
                    result[ym]["results"][s] = []
                cur_date = s
                cur_ym = ym
                continue

            m = regex_street.match(elem2)
            if m:
                if cur_ym is None or cur_date is None:
                    print("error%s" % str(elem2))
                    continue
                for elem3 in elem2.split(","):
                    result[cur_ym]["results"][cur_date].append(elem3.strip())

if not os.path.isdir("results"):
    os.mkdir("results")

for ym, data in result.items():
    json.dump(
        data,
        open("results/%s.json" % ym, "w"),
        indent="    "
    )