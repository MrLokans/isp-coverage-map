import re

import requests

from .base import BaseParser
from ..point import Point


class MTS_Parser(BaseParser):
    PARSER_NAME = "MTS"
    PARSER_URL = "http://www.mts.by"
    MTS_MAP_URL = "http://www.mts.by/home/connect/"
    YA_MAPS_POINT_REGEX = r"var placemark(?P<id>[\d]+) = new YMaps.Placemark\(new YMaps\.GeoPoint\((?P<long>[\d]+\.[\d]+),(?P<lat>[\d]+\.[\d]+)"
    YA_MAPS_POINT_NAME_REGEX = r'placemark(?P<id>[\d]+)\.name = "(?P<name>[^\']*)";'
    YA_MAPS_POINT_DESCRIPTION_REGEX = r'placemark(?P<id>[\d]+)\.description = "(?P<description>[^\']*)";'

    def __init__(self, *args, **kwargs):
        pass

    def _extract_point_name(self, point_id):
        pass

    def _coordinates_from_map(self, page_content):
        return ((c[1], c[2]) for c in re.finditer(self.YA_MAPS_POINT_REGEX,
                                                  page_content))

    def get_points(self):
        """Parse MTS site and extract points from map"""
        r = requests.get(self.MTS_MAP_URL)
        return (Point(*c, "") for c in self._get_coordinates_from_map(r.text))


if __name__ == '__main__':
    parser = MTS_Parser()
    dots = parser.get_points()
