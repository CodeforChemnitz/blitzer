#!/usr/bin/env python
# -*- coding: utf-8 -*-

import overpy, overpy.helper, os, json, datetime, decimal


class DecimalJSONEncoder(json.JSONEncoder):
    """
    DecimalJSONEncoder that knows how to encode decimal types.
    """
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        else:
            return super(DecimalJSONEncoder, self).default(o)


def parse_date(dataList):
        """
        Parse an dict with following structure:

        {
                '2014-05-01': ['street 1', 'street 2', 'street3'],
                ...
        }
        :param dataList:
        :return: geojson string
        """
        geojson = {
                "type": "FeatureCollection",
                "features": []
        }

        for date_string, streets in dataList.items():
                date = datetime.datetime.strptime(date_string,
                                                  '%Y-%m-%d').date()
                if str(date) != date_string:
                        print("error: date parsing failed:", date, date_string)
                print(date, streets)

                for street in streets:
                        result = overpy.helper.get_street(street,
                                                          "3600062594", api)

                        coordinates = []
                        for way in result.get_ways():
                                way_list = [[node.lon, node.lat] for node in way.get_nodes()]
                                if len(way_list) >= 2:
                                        coordinates.append(way_list)
                                else:
                                        print("insufficient way nodes", way)

                        if coordinates == []:
                                print("coordinates empty for", street)
                                continue

                        geojson["features"].append({
                                "type": "Feature",
                                "geometry": {
                                        "type": "MultiLineString",
                                        "coordinates": coordinates
                                },
                                "properties": {
                                        "date": str(date),
                                        "name": street
                                }
                        })

        return json.dumps(geojson, cls=DecimalJSONEncoder, sort_keys=True, indent=4)

path = "results/"
api = overpy.Overpass()

for f in os.listdir(path):
        if f[-8:] == '.geojson':
                continue

        filepath = os.path.join(path, f)
        print("current file is:", filepath)

        # skip files with existing results
        if os.path.exists(filepath.replace('json', 'geojson')):
                continue

        with open(filepath, "r") as fh:
                data = json.load(fh)

        # parse it
        geojson = parse_date(data["results"])

        with open(filepath.replace('json', 'geojson'), 'w') as wfh:
                wfh.write(geojson)
