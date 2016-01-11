# TODO: parse descriptions, show only active

import re
import csv

import requests

MTS_MAP_URL = "http://www.mts.by/home/connect/"

YA_MAPS_POINT_REGEX = r"var placemark(?P<id>[\d]+) = new YMaps.Placemark\(new YMaps\.GeoPoint\((?P<long>[\d]+\.[\d]+),(?P<lat>[\d]+\.[\d]+)"


def unescape_text(text):
    unescaped = text.replace(r"\x3c", "<").replace(r"\x3e", ">")
    unescaped = unescaped.replace(r"\x3d", "=")
    unescaped = unescaped.replace(r"\x26quot;", "&")
    return unescaped


def main():
    r = requests.get(MTS_MAP_URL)
    matches = [x for x in re.findall(YA_MAPS_POINT_REGEX, r.text)]
    with open('mts.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["longitude", "latitude"])
        for _, longitude, latitude in matches:
            writer.writerow([longitude, latitude])


def get_map_points(map_json):
    return []


if __name__ == '__main__':
    main()
