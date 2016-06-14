import re

import requests

from .base import BaseParser
from .point import Point


class MTS_Parser(BaseParser):
    PARSER_NAME = "MTS"
    PARSER_URL = "http://www.mts.by"
    MTS_MAP_URL = "http://www.mts.by/home/connect/"
    YA_MAPS_POINT_REGEX = r"var placemark(?P<id>[\d]+) = new YMaps.Placemark\(new YMaps\.GeoPoint\((?P<long>[\d]+\.[\d]+),(?P<lat>[\d]+\.[\d]+)"

    def get_points(self):
        """Parse MTS site and extract points from map"""
        r = requests.get(self.MTS_MAP_URL)
        matches = (x for x in re.findall(self.YA_MAPS_POINT_REGEX, r.text))
        return [Point(long, lat, "") for _, long, lat in matches]


if __name__ == '__main__':
    parser = MTS_Parser()
    dots = parser.get_points()
