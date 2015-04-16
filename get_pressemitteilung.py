#!/usr/bin/env python
import urllib.request
from io import BytesIO
from lxml import etree
import json

data = urllib.request.urlopen("http://www.chemnitz.de/chemnitz/de/aktuelles/presse/pressemitteilungen/presse.itl?search=1&q=Geschwindigkeitskontrollen&archiv=1").read()
base_url = "http://www.chemnitz.de/chemnitz/de/aktuelles/presse/pressemitteilungen/"

parser = etree.HTMLParser()
tree = etree.parse(BytesIO(data), parser)

results = []
for elem in tree.xpath("//div[@id='col2_content']"):
    for elem2 in elem.xpath("descendant-or-self::*/a"):
        results.append({
            "url": base_url + elem2.attrib["href"],
            "title": elem2.attrib["title"]
        })

json.dump(
    results,
    open("pressemitteilungen.json", "w"),
    indent="    "
)