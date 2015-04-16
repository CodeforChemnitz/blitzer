#!/usr/bin/env python

import urllib.request
from io import StringIO, BytesIO
import re

from lxml import etree

import overpy

import geojson
from geojson import FeatureCollection, LineString, Feature

data = urllib.request.urlopen("http://www.chemnitz.de/chemnitz/de/aktuelles/presse/pressemitteilungen/2015/95.html").read()

parser = etree.HTMLParser()

tree = etree.parse(BytesIO(data), parser)

l = {}

regex_date = re.compile("^\w+, (?P<day>\d+)\.(?P<month>\d+)\.(?P<year>\d+)")
regex_street = re.compile("^\w+")

result = {}

cur_date = None
for elem in tree.xpath("//div[@id='col2_content']/div[2]/div"):
    for elem2 in elem.xpath("descendant-or-self::*/text()"):
        m = regex_date.match(elem2)
        if m:
            s = "%s-%s-%s" % (m.group("year"), m.group("month"), m.group("day"))
            if s not in result:
                result[s] = []
            cur_date = s
            continue

        m = regex_street.match(elem2)
        if m:
            for elem3 in elem2.split(","):
                result[cur_date].append(elem3.strip())

import pprint
pprint.pprint(result)

api = overpy.Overpass()

query = """
[out:json]
[timeout:25]
;
area(3600062594)->.area;
(  way
    ["name"="%s"]
    ["highway"]
    (area.area);
   -
   (
    way
      ["highway"="service"]
      (area.area);
    way
      ["highway"="track"]
      (area.area);
  );
);
out body;
>;
out skel qt;
"""

r = []

for k, v in result.items():
    for street in v:
        result = api.query(query % (street,))
        for line in result.ways:
            points = []
            for p in line.nodes:
                points.append((float(p.lon), float(p.lat)))
            r.append(Feature(geometry=LineString(points)))

geo = FeatureCollection(r)
geojson.dumps(geo)

fp = open("/tmp/geo.json", "w+")
fp.write(geojson.dumps(geo))
fp.close()
